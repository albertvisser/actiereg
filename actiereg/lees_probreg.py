"""acties met bijbehorende events met juiste datum kopieren naar actiereg db
"""

## import sqlite3 as sql
from probreg import dml
import probreg.dml_sql as sql


def add_data(fnaam):
    """Probreg acties van een project (file) overnemen in ActieReg db
    """
    pnaam = fnaam.join(("/home/visser/Python/probreg_data/", ".xml"))
    ## con = sql.connect("/home/visser/www/actiereg/actiereg.db")
    data = [actie[0] for actie in dml.Acties(pnaam, arch="alles").lijst]
    actie_id = 4
    for item in data:
        actie = dml.Actie(pnaam, item)
        if actie.status == "":
            actie.status = " "
        actie_id += 1
        nieuw = sql.Actie(fnaam, 0)
        nieuw.id, nieuw.datum, = actie.id, actie.datum,
        nieuw.titel = " - ".join(actie.titel.split(": ", 1))
        nieuw.status, nieuw.soort, nieuw.arch = actie.status, actie.soort, actie.arch
        nieuw.updated = actie.updated
        nieuw.melding, nieuw.oorzaak = actie.melding, actie.oorzaak
        nieuw.oplossing, nieuw.vervolg = actie.oplossing, actie.vervolg
        nieuw.events = actie.events
        nieuw.list()
        nieuw.write()


def modify_data(pnaam):
    """Probreg acties van een project (file) aanpassen (?) in ActieReg db
    """
    fnaam = pnaam.join(("/home/visser/Python/probreg_data/", ".xml"))
    if pnaam == "probreg":
        pnaam += "_pc"
    con = sql.connect("/home/albert/www/actiereg/actiereg.db")
    data = [actie[0] for actie in dml.Acties(fnaam, arch="alles").lijst]
    for item in data:
        ## print(item)
        actie = dml.Actie(pnaam, item)
        # datums goed zetten
        if " " not in actie.updated:
            actie.updated += " 00:00:00"
        cmd = "select id from {0}_actie where nummer = ?".format(pnaam)
        ## print cmd, actie.id
        get = con.execute(cmd, (actie.id,))
        for x in get:
            sql_actie_id = x[0]
        ## cmd = "update {0}_actie set start = ?, gewijzigd = ? where id = ?".format(pnaam)
        ## print cmd, actie.datum, actie.updated, sql_actie_id
        ## con.execute(cmd,(actie.datum, actie.updated, sql_actie_id))
        ## con.commit()
        cmd = "select id,start,text from {}_event where actie_id = ?".format(pnaam)
        ## print cmd, sql_actie_id
        get = [x for x in con.execute(cmd, (sql_actie_id,))]
        evt_data = (x for x in get)
        for start, text in actie.events:
            if not text:
                text = ""
            try:
                sql_evt_id, sql_evt_start, sql_evt_text = evt_data.next()
            except StopIteration:
                print("Geen sql events (meer) voor actie {}".format(sql_actie_id))
                break
            cmd = "update {}_event set start = ? where id = ?".format(pnaam)
            if text == sql_evt_text:
                # datum goed zetten
                try:
                    con.execute(cmd, (start, sql_evt_id))
                except:
                    raise
                print(cmd, start, sql_evt_id)
            con.commit()

if __name__ == "__main__":
    add_data("doctool")
    ## modify_data("doctool")
