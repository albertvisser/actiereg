"""Sample data for initially populating a project
"""


class Status(object):
    """gemeld, in behandeling, afgehandeld e.d."""
    def __init__(self, **args):
        self.id = args.get("id", "0")
        self.title = args.get("title", "")
        self.value = args.get("value", "0")
        self.order = args.get("order", "0")


class Soort(object):
    """probleem, wens e.d."""
    def __init__(self, **args):
        self.id = args.get("id", "0")
        self.title = args.get("title", "")
        self.value = args.get("value", "0")
        self.order = args.get("order", "0")


class Page(object):
    """titels voor de links/onderdelen"""
    def __init__(self, **args):
        self.id = args.get("id", "0")
        self.title = args.get("title", "")
        self.link = args.get("link", "")
        self.order = args.get("order", "0")


class Actie(object):
    """primaire gegevenstabel"""
    def __init__(self, **args):
        self.id = args.get("id", "0")
        self.nummer = args.get("nummer", "")
        self.start = args.get("start", "")
        self.about = args.get("about", "")
        self.title = args.get("title", "")
        self.gewijzigd = args.get("gewijzigd", "")
        self.soort = args.get("soort", "0")
        self.status = args.get("status", "0")
        self.arch = args.get("arch", "")
        self.melding = args.get("melding", "")
        self.oorzaak = args.get("oorzaak", "")
        self.oplossing = args.get("oplossing", "")
        self.vervolg = args.get("vervolg", "")


class Event(object):
    """historische gegevens over een actie"""
    def __init__(self, **args):
        self.id = args.get("id", "0")
        self.actie = args.get("actie", "1")
        self.start = args.get("start", "")
        self.text = args.get("text", "")

soort_list = [
    Soort(id="1", value="0", title="onbekend"),
    Soort(id="2", value="1", title="probleem"),
    Soort(id="3", value="2", title="wens"), ]

stat_list = [
    Status(id="1", value="0", title="gemeld"),
    Status(id="2", value="1", title="in behandeling"),
    Status(id="3", value="2", title="opgelost/afgehandeld"), ]

page_list = [
    Page(id="1", link="index", title="actielijst"),
    Page(id="2", link="start", title="details"),
    Page(id="3", link="meld", title="melding"),
    Page(id="4", link="oorz", title="oorzaak"),
    Page(id="5", link="opl", title="oplossing"),
    Page(id="6", link="verv", title="vervolg"),
    Page(id="7", link="voortg", title="voortgang"), ]

actie_list = [
    Actie(
        id="1",
        nummer="2009-0001",
        start="13-09-2009 12:15:00",
        about="bv. gedumpte job",
        title="wat er mis is of verbeterd moet worden",
        gewijzigd="13-09-2009 12:16:05",
        soort="1",
        status="0",
        arch=False,
        melding="zo uitgebreid mogelijke beschrijving van de situatie, "
                "bij voorkeur vergezeld van een opsommin van de voorafgaande "
                "handelingen en de foutmelding(en) die erop gevolgd zijn; "
                "dan wel een uitbebreide beschrijving van de gewenste "
                "situatie.",
        oorzaak="het veld 'oorzaak' heet zo omdat het oorspronkelijk alleen "
                "bedoeld was om de omstandigheden en oorzaak van een gemeld "
                "probleem nader te beschrijven, maar kan natuurlijk ook gebruikt "
                "worden om een analyse van een wens in vast te leggen.",
        oplossing="beschrijving van de gekozen oplossing",
        vervolg="alleen invullen als er vervolgacties moeten worden ondernomen", ),
    Actie(
        id="1",
        nummer="2009-0001",
        start="13-09-2009 12:15:00",
        about="bv. gedumpte job",
        title="wat er mis is of verbeterd moet worden",
        gewijzigd="13-09-2009 12:16:05",
        soort="1",
        status="0",
        arch=False,
        melding="applicatie voor het vastleggen en volgen van acties gewenst",
        oorzaak="het veld 'oorzaak' heet zo omdat het oorspronkelijk alleen "
                "bedoeld was om de omstandigheden en oorzaak van een gemeld "
                "probleem nader te beschrijven, maar kan natuurlijk ook gebruikt "
                "worden om een analyse van een wens in vast te leggen",
        oplossing="beschrijving van de gekozen oplossing",
        vervolg="alleen invullen als er vervolgacties moeten worden ondernomen", ),
    Actie(
        id="1",
        nummer="2009-0001",
        start="13-09-2009 12:15:00",
        about="bv. gedumpte job",
        title="wat er mis is of verbeterd moet worden",
        gewijzigd="13-09-2009 12:16:05",
        soort="1",
        status="0",
        arch=False,
        melding="applicatie voor het vastleggen en volgen van acties gewenst",
        oorzaak="het veld 'oorzaak' heet zo omdat het oorspronkelijk alleen "
                "bedoeld was om de omstandigheden en oorzaak van een gemeld "
                "probleem nader te beschrijven, maar kan natuurlijk ook gebruikt "
                "worden om een analyse van een wens in vast te leggen",
        oplossing="beschrijving van de gekozen oplossing",
        vervolg="alleen invullen als er vervolgacties moeten worden ondernomen", ), ]

event_list = [
    Event(
        id="3",
        start="13-09-2009 12:17:00",
        text="actie nogmaals gewijzigd", ),
    Event(
        id="2",
        start="13-09-2009 12:16:00",
        text="actie gewijzigd", ),
    Event(
        id="1",
        start="13-09-2009 12:15:00",
        text="actie opgevoerd", ), ]
