<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" type="text/css" href="stylesheet.css">
    <title>extrovert</title>
</head>

<?php
$servername = "mysql.stud.ntnu.no";
$username = "olaliu_tdt4140";
$password = "olaliu_tdt4140";
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
    <div id="knapper">
        <button class="button" style="vertical-align:middle" ><span><?php echo $rowcount ?></span></button>
    </div>
</body>
</html>
