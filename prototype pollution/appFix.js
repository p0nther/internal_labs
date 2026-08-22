const express = require("express");

const app = express();

app.use(express.json());

function merge(target, source) {

    for (let key in source) {

        if (
            key === "__proto__" ||
            key === "constructor" ||
            key === "prototype"
        ) {
            continue;
        }

        if (
            typeof source[key] === "object" &&
            source[key] !== null
        ) {

            if (!target[key]) {
                target[key] = {};
            }

            merge(target[key], source[key]);

        } else {

            target[key] = source[key];
        }
    }

    return target;
}

app.post("/update", (req, res) => {

    const settings = {};

    merge(settings, req.body);

    res.json({
        merged: settings
    });
});

app.listen(3000, () => {
    console.log("Running on http://127.0.0.1:3000");
});
