<!DOCTYPE html>
<html>
<?php
$servername = "mysql.stud.ntnu.no";
$username = "olaliu_tdt4140";
$password = "olaliu_tdt4140";
$dbname = "olaliu_tdt4140database";

// Create connection
$conn = mysqli_connect($servername, $username, $password, $dbname);

$sql = "INSERT INTO student(exist)
	VALUES ('1')";

if ($conn->query($sql) === FALSE) {
    echo "Error: " . $sql . "<br>" . $conn->error;
}
$sq2 = "Select * from student";

$result = mysqli_query($conn,$sq2);
$rowcount = mysqli_num_rows($result);
echo $rowcount;

$conn->close();
?>

</html>
