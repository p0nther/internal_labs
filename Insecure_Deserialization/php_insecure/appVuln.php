<?php

if (php_sapi_name() === 'cli') {

    echo "[+] Starting server on http://127.0.0.1:8000\n";

    passthru(
        "php -S 127.0.0.1:8000 " . __FILE__
    );

    exit;
}

class User
{
    public $username = "guest";
    public $role = "user";
}

class Logger
{
    public $file;
    public $content;

    public function __destruct()
    {
        file_put_contents(
            $this->file,
            $this->content
        );
    }
}

$result = "";

if (($_SERVER["REQUEST_METHOD"] ?? "") === "POST") {

    try {

        $data = $_POST["data"] ?? "";

        $obj = unserialize(
            base64_decode($data)
        );

        $result = print_r($obj, true);

    } catch (Throwable $e) {

        $result = $e->getMessage();
    }
}

?>

<!DOCTYPE html>
<html>
<head>
    <title>Insecure Deserialization Lab</title>
</head>
<body>

<h1>PHP Insecure Deserialization Lab</h1>

<form method="POST">
<textarea name="data" rows="10" cols="80"></textarea>
<br><br>
<button type="submit">
Deserialize
</button>
</form>

<?php if ($result): ?>
<hr>
<pre><?= htmlspecialchars($result) ?></pre>
<?php endif; ?>

</body>
</html>
