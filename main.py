import json
import datetime
import xml.etree.ElementTree
from bclib import edge
# import edge


options = {
    "server": "127.0.0.1:1564",
    "sender": "127.0.0.1:1025",
    "receiver": "127.0.0.1:1026",
    "router": {
        "client_source": ["/source"],
        "restful": ["/rest"],
        "web": ["*"],
    }
}

app = edge.from_options(options)

app.cache()

def generate_data() -> list:
    import string
    import random  # define the random module

    ret_val = list()
    for i in range(10):
        ret_val.append({"id": i, "data": ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=10))})
    return ret_val


@app.client_source_action(
    app.equal("context.command.source", "basiscore"),
    app.in_list("context.command.mid", "10", "20"))
def process_basiscore_source(context: edge.ClientSourceContext):
    print("process_basiscore_source")
    return generate_data()


@app.client_source_action(
    app.equal("context.command.source", "demo"),
    app.in_list("context.command.mid", "10", "20"))
def process_demo_source(context: edge.ClientSourceContext):
    return [row for row in generate_data() if row["id"] < 5]


@app.client_source_member_action(
    app.equal("context.member.name", "list")
)
def process_list_member(context: edge.ClientSourceMemberContext):
    print("process_list_member")
    return context.data


@app.client_source_member_action(
    app.equal("context.member.name", "paging")
)
def process_page_member(context: edge.ClientSourceMemberContext):
    data = {
        "total": len(context.data),
        "from": 0,
        "to": len(context.data)-1,
    }
    print("process_page_member")
    return data


@app.client_source_member_action(
    app.equal("context.member.name", "count")
)
def process_count_member(context: edge.ClientSourceMemberContext):
    data = {
        "count": len(context.data)
    }
    print("process_count_member")
    return data


@app.web_action(
    app.url("nill-test/mysample-source/:id"))
def process_web_sample_source_request(context: edge.WebContext):
    id = int(context.url_segments.id)
    return f"""
     <basis core="dbsource" run="atclient" source="basiscore" mid="20" name="demo"  lid="1" dmnid="" ownerpermit="" >
        <member name="list" type="list" pageno="3" perpage="20" request="catname" order="id desc"></member>
        <member name="paging" type="list" request="paging" count="5" parentname="list"></member>
        <member name="count" type="scalar" request="count" ></member>
     </basis>

    <basis core="callback" run="AtClient" triggers="demo.list demo.paging demo.count" method="onSource"></basis>
<h1>Press F12 for visit result in console</h1>
<h2 id="naz"> </h2>
    <script>
        var host = {{
            debug: false,
            autoRender: true,
            'DbLibPath': '/alasql.min.js',
            settings: {{
                'connection.web.basiscore': 'http://localhost:1564/qam-test/source',

                'default.dmnid': 2668,
            }},

        }}


        function onSource(args) {{
            console.log("Amin {id}");
            console.table(args.source.rows["{id}"].data);
            document.getElementById("naz").innerHTML = args.source.rows["{id}"].data;
        }}
    </script>
    <script src="https://cdn.basiscore.net/_js/basiscore-2.4.11.min.js"></script>
        """

app.listening()
