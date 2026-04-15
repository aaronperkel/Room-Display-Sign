# src/database.py
import os
from mysql.connector import connect, Error
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    cfg = dict(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
    )

    use_ssl = os.getenv("DB_USE_SSL", "false").lower() in ("1", "true", "yes")
    ca_path = os.getenv("DB_SSL_CA_PATH")
    if use_ssl and ca_path:
        cfg["ssl_ca"] = ca_path
        cfg["ssl_verify_cert"] = True

    try:
        return connect(**cfg)
    except Error as e:
        print(f"[ERROR] DB connect: {e}")
        return None

def get_unpaid_bills_summary():
    """
    Returns (person_totals, total_outstanding)

    person_totals: list of dicts -> { personName, totalOwedByPerson }
      - Sum of per-person shares (u.fldCost) for *unpaid* bills where that person
        still appears in tblBillOwes.

    total_outstanding: float
      - Sum of all remaining per-person shares across all unpaid bills.
        (Equivalent to summing u.fldCost for every row still present in tblBillOwes.)
    """
    conn = get_db_connection()
    if not conn:
        return None, 0.0

    try:
        cur = conn.cursor(dictionary=True)

        # Overall outstanding = sum of remaining per-person shares
        cur.execute("""
            SELECT COALESCE(SUM(u.fldCost), 0) AS totalOutstanding
            FROM tblUtilities u
            JOIN tblBillOwes bo ON u.pmkBillID = bo.billID
            WHERE u.fldStatus = 'Unpaid';
        """)
        total_outstanding = float((cur.fetchone() or {}).get("totalOutstanding") or 0.0)

        # Per-person totals = sum of per-person shares for that person still owing
        cur.execute("""
            SELECT
                p.personName,
                COALESCE(SUM(u.fldCost), 0) AS totalOwedByPerson
            FROM tblUtilities u
            JOIN tblBillOwes bo ON u.pmkBillID = bo.billID
            JOIN tblPeople p ON bo.personID = p.personID
            WHERE u.fldStatus = 'Unpaid'
            GROUP BY p.personName
            ORDER BY p.personName;
        """)
        person_totals = cur.fetchall()

        return person_totals, total_outstanding

    except Error as e:
        print(f"[ERROR] DB query: {e}")
        return None, 0.0
    finally:
        try:
            cur.close()
            conn.close()
        except Exception:
            pass

def get_detailed_unpaid_bills():
    """
    Returns a list of dicts, each row a remaining per-person obligation for an unpaid bill.
    Useful if you want to show who still owes on each specific bill.
    """
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT
                u.pmkBillID    AS billID,
                u.fldItem      AS item,
                u.fldTotal     AS billTotal,
                u.fldCost      AS perPersonCost,
                u.fldDue       AS dueDate,
                p.personName   AS personOwing
            FROM tblUtilities u
            JOIN tblBillOwes bo ON u.pmkBillID = bo.billID
            JOIN tblPeople p ON bo.personID = p.personID
            WHERE u.fldStatus = 'Unpaid'
            ORDER BY u.fldDue, u.pmkBillID, p.personName;
        """)
        return cur.fetchall()

    except Error as e:
        print(f"[ERROR] DB detail query: {e}")
        return None
    finally:
        try:
            cur.close()
            conn.close()
        except Exception:
            pass