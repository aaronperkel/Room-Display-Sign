<?php
// eink-display.php
// This script fetches utility bill information and formats it for an e-ink display.

// Set the header to plain text for clean output
header('Content-Type: text/plain');

// Include the database connection script.
// The script will die with an error message if the connection fails.
require_once __DIR__ . '/connect-DB.php';

echo "---------------------------------\n";
echo "    Monthly Utilities Status\n";
echo "---------------------------------\n";
echo "Generated on: " . date('Y-m-d H:i:s') . "\n\n";

try {
    // --- 1. Get Total Amount Due ---
    $totalDueStmt = $pdo->query("SELECT SUM(fldTotal) AS totalDue FROM tblUtilities WHERE fldStatus = 'Unpaid'");
    $totalDue = $totalDueStmt->fetch(PDO::FETCH_ASSOC)['totalDue'] ?? 0.00;

    printf("Total Amount Due: $%.2f\n", $totalDue);
    echo "---------------------------------\n\n";

    // --- 2. Get Total Owed Per Person ---
    $perPersonStmt = $pdo->query("
        SELECT
            p.personName,
            SUM(u.fldCost) AS totalOwedByPerson
        FROM tblUtilities u
        JOIN tblBillOwes bo ON u.pmkBillID = bo.billID
        JOIN tblPeople p ON bo.personID = p.personID
        WHERE u.fldStatus = 'Unpaid'
        GROUP BY p.personName
        ORDER BY p.personName
    ");

    $perPersonTotals = $perPersonStmt->fetchAll(PDO::FETCH_ASSOC);

    if ($perPersonTotals) {
        echo "Summary of What Each Person Owes:\n";
        foreach ($perPersonTotals as $person) {
            printf("- %-10s: $%6.2f\n", $person['personName'], $person['totalOwedByPerson']);
        }
        echo "\n";
    } else {
        echo "No outstanding amounts owed by anyone. All settled up!\n\n";
    }

    // --- 3. Get Detailed List of Unpaid Bills ---
    $detailedStmt = $pdo->query("
        SELECT
            u.fldItem,
            u.fldTotal,
            u.fldCost,
            u.fldDue,
            GROUP_CONCAT(p.personName ORDER BY p.personName SEPARATOR ', ') AS peopleOwing
        FROM tblUtilities u
        JOIN tblBillOwes bo ON u.pmkBillID = bo.billID
        JOIN tblPeople p ON bo.personID = p.personID
        WHERE u.fldStatus = 'Unpaid'
        GROUP BY u.pmkBillID
        ORDER BY u.fldDue
    ");

    $unpaidBills = $detailedStmt->fetchAll(PDO::FETCH_ASSOC);

    if ($unpaidBills) {
        echo "---------------------------------\n";
        echo "Details of Unpaid Bills:\n";
        echo "---------------------------------\n\n";

        foreach ($unpaidBills as $bill) {
            printf("Bill: %s (Total: $%.2f)\n", $bill['fldItem'], $bill['fldTotal']);
            printf("Due Date: %s\n", $bill['fldDue']);
            printf("Cost per Person: $%.2f\n", $bill['fldCost']);
            printf("Owed by: %s\n", $bill['peopleOwing']);
            echo "--------------------------\n";
        }
    } else {
        echo "---------------------------------\n";
        echo "No unpaid bills found. Great job!\n";
        echo "---------------------------------\n";
    }

} catch (PDOException $e) {
    // Output a user-friendly error message
    echo "\n---------------------------------\n";
    echo "   ERROR FETCHING UTILITY DATA\n";
    echo "---------------------------------\n";
    echo "Could not retrieve data from the database.\n";
    echo "Error: " . htmlspecialchars($e->getMessage()) . "\n";

    // Log the detailed error to the server's error log
    error_log("E-ink Display Script Error: " . $e->getMessage());
}

?>
