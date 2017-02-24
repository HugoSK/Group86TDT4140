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

$sql = "INSERT INTO student(exist)
	VALUES ('1')";

if ($conn->query($sql) === FALSE) {
    echo "Error: " . $sql . "<br>" . $conn->error;
}

$conn->close();
?>
</html>
