+from django.contrib.auth.decorators import login_required
+import actiereg._basic.models as my
+ROOT = "basic"
+NAME = "demo"
+import actiereg.core as core
+
+def koppel(request):
+    return core.koppel(ROOT,my,request)
+
+@login_required
+def index(request):
+    return core.index(ROOT,NAME,my,request)
+
+@login_required
+def settings(request):
+    return core.settings(ROOT,NAME,my,request)
+
+@login_required
+def setusers(request):
+    return core.setusers(ROOT,my,request)
+
+@login_required
+def settabs(request):
+    return core.settabs(ROOT,my,request)
+
+@login_required
+def settypes(request):
+    return core.settypes(ROOT,my,request)
+
+@login_required
+def setstats(request):
+    return core.setstats(ROOT,my,request)
+
+@login_required
+def select(request):
+    return core.select(ROOT,NAME,my,request)
+
+@login_required
+def setsel(request):
+    return core.setsel(ROOT,my,request)
+
+@login_required
+def order(request):
+    return core.order(ROOT,NAME,my,request)
+
+@login_required
+def setorder(request):
+    return core.setorder(ROOT,my,request)
+
+@login_required
+def detail(request,actie=""):
+    return core.detail(ROOT,NAME,my,request,actie)
+
+@login_required
+def wijzig(request,actie="",doe=""):
+    return core.wijzig(ROOT,my,request,actie,doe)
+
+@login_required
+def tekst(request,actie="",page=""):
+    return core.tekst(ROOT,NAME,my,request,actie,page)
+
+@login_required
+def wijzigtekst(request,actie="",page=""):
+    return core.wijzigtekst(ROOT,my,request,actie,page)
+
+@login_required
+def events(request,actie="",event=""):
+    return core.events(ROOT,NAME,my,request,actie,event)
+
+@login_required
+def wijzigevents(request,actie="",event=""):
+    return core.wijzigevents(ROOT,my,request,actie,event)
