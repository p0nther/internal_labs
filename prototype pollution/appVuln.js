const express = require("express");

const app = express();

app.use(express.urlencoded({ extended: true }));

app.get("/", (req, res) => {

    const user = {};

    res.send(`
        <h1>Prototype Pollution Lab Vuln</h1>

        <form method="POST" action="/update">
            Key:
            <input name="key">
            <br><br>

            Value:
            <input name="value">
            <br><br>

            <button>Submit</button>
        </form>

        <hr>

        <p>isAdmin = ${user.isAdmin}</p>

        <a href="/admin">Admin Panel</a>
    `);
});

app.post("/update", (req, res) => {

    const key = req.body.key;
    const value = req.body.value;

    // VULNERABLE
    Object.prototype[key] = value;

    res.send(`
        Pollution Applied

        <br><br>

        <a href="/">Back</a>
    `);
});

app.get("/admin", (req, res) => {

    const user = {};

    if (user.isAdmin) {
        return res.send("<h1>Admin Access Granted</h1>");
    }

    res.send("<h1>Access Denied</h1>");
});

app.listen(5000, () => {
    console.log("http://127.0.0.1:5000");
});
