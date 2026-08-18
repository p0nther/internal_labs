from flask import Flask, request
from lxml import etree

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return """
    <h2>XXE Fixed Lab</h2>
    <form method="POST" action="/parse">
        <textarea name="xml" rows="15" cols="80"></textarea><br>
        <button type="submit">Parse XML</button>
    </form>
    """

@app.route("/parse", methods=["POST"])
def parse_xml():
    xml_data = request.form.get("xml", "")

    try:
        parser = etree.XMLParser(
            resolve_entities=False,
            load_dtd=False,
            no_network=True
        )

        root = etree.fromstring(xml_data.encode(), parser)

        return f"""
        <h3>Parsed Successfully</h3>
        <pre>{etree.tostring(root, pretty_print=True).decode()}</pre>
        """

    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(debug=True)
