const express = require("express");

const app = express();

app.use(express.urlencoded({ extended: true }));

// Prevent modifications to Object.prototype
Object.freeze(Object.prototype);

app.get("/", (req, res) => {

    // Object with no prototype
    const user = Object.create(null);

    res.send(`
        <h1>Prototype Pollution - Fixed</h1>

        <form method="POST" action="/update">

            Key:
            <input name="key">

            <br><br>

            Value:
            <input name="value">

            <br><br>

            <button>
                Submit
            </button>

        </form>

        <hr>

        <p>isAdmin = ${user.isAdmin}</p>

        <a href="/admin">
            Admin Panel
        </a>
    `);
});

app.post("/update", (req, res) => {

    const key = req.body.key;
    const value = req.body.value;

    const blocked = [
        "__proto__",
        "prototype",
        "constructor"
    ];

    if (blocked.includes(key)) {

        return res.send(`
            Dangerous key blocked!
            <br><br>
            <a href="/">Back</a>
        `);
    }

    try {

        // Attempted pollution will fail because
        // Object.prototype is frozen
        Object.prototype[key] = value;

    } catch (e) {

        console.log("Blocked:", e.message);

    }

    res.send(`
        Property saved
        <br><br>
        <a href="/">Back</a>
    `);
});

app.get("/admin", (req, res) => {

    // No prototype chain
    const user = Object.create(null);

    if (user.isAdmin) {

        return res.send(`
            <h1>Admin Access Granted</h1>
        `);
    }

    res.send(`
        <h1>Access Denied</h1>
    `);
});

app.listen(3000, () => {

    console.log(
        "http://127.0.0.1:3000"
    );

});
