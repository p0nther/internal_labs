<?php
if (php_sapi_name() === 'cli') {

    echo "[+] Starting server on http://127.0.0.1:8000\n";

    passthru(
        "php -S 127.0.0.1:8001 " . __FILE__
    );

    exit;
}

$result = "";

if ($_SERVER["REQUEST_METHOD"] === "POST") {

    $data = $_POST["data"] ?? "";

    try {

        $obj = json_decode(
            $data,
            true,
            512,
            JSON_THROW_ON_ERROR
        );

        $result = print_r($obj, true);

    } catch (Exception $e) {

        $result = $e->getMessage();
    }
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>Secure Deserialization Lab</title>
</head>
<body>

<h1>Secure Version</h1>

<form method="POST">

<textarea name="data" rows="10" cols="80"></textarea>

<br><br>

<button type="submit">
Parse
</button>

</form>

<?php if($result): ?>

<h3>Output</h3>

<pre><?= htmlspecialchars($result) ?></pre>

<?php endif; ?>

</body>
</html>
