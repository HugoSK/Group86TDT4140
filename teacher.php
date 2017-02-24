<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" type="text/css" href="stylesheet.css">
    <title>extrovert</title>
</head>

<?php
$servername = "mysql.stud.ntnu.no";
$username = "o...";
$password = "o...";
$dbname = "olaliu_tdt4140database";

// Create connection
$conn = mysqli_connect($servername, $username, $password, $dbname);

$sq2 = "Select * from student";

$result = mysqli_query($conn,$sq2);
$rowcount = mysqli_num_rows($result);

$conn->close();
?>
<body>
    <div ID="header">Extrovert</div>
    <div id="counter">
        <p>Antall studenter som syns du er for rask: </p>
        <?php echo $rowcount ?>
    </div>
</body>
</html>
