"""unittests for newapp mdule
"""
import os
import shutil
import pathlib
import difflib
import pytest
import actiereg.newapp as newapp


def get_contents_for_compare(path):
    "read contents of specified file"
    return [x + '\n' for x in path.read_text().split('\n')]


class TestCopyOver:
    """test copyover varianten"""

    def test_project_filenames(self):
        "trying out all listed filenames"
        where = newapp.BASE / 'test'
        where.mkdir()
        testobj = newapp.NewProj()
        for name in newapp.ROOT_FILES:
            testobj.copyover(name)
            path = where / name
            oldpath = newapp.BASE / '_basic' / name
            assert path.exists()  # file copied
            if name in newapp.SYMLINK:
                # test of er een symlink gemaakt is
                assert path.is_symlink()  # path is not a symlink
                assert os.readlink(str(path)) == str(oldpath)  # path points to the right file
            else:
                # test of file gekopieerd is inclusief correcte edits
                data = path.read_text().replace('_basic', name)
                data = data.replace('basic', name).replace('demo', 'gargl')
                assert path.read_text() == data   # contents correctly copied
        for path in where.iterdir():
            path.unlink()
        where.rmdir()


class TestBackup:
    "test backup functie"

    def test_using_none(self):
        "test for filename is None"
        testobj = newapp.NewProj()
        with pytest.raises(TypeError):
            testobj.backup(pathlib.Path(None))
        assert not os.path.exists('None~')

    def test_empty_filename(self):
        "test for empty filename"
        testobj = newapp.NewProj()
        with pytest.raises(OSError):
            testobj.backup(pathlib.Path(''))
        assert not os.path.exists('~')

    def test_nonexistant_file(self):
        "test for nonexistant file"
        testobj = newapp.NewProj()
        path = pathlib.Path('kloenk')
        if path.exists():
            path.unlink()
        with pytest.raises(FileNotFoundError):
            testobj.backup(path)

    def test_backup(self):
        "test for existing file"
        testobj = newapp.NewProj()
        path = pathlib.Path('kloenk')
        if not path.exists():
            path.touch()
        testobj.backup(path)
        assert not os.path.exists('kloenk')  # huh?
        assert os.path.exists('kloenk~')


class TestParseArgs:
    def test_messages(self):
        "test situations that produce error messages"
        assert newapp.NewProj('whatever').msg == 'project niet gevonden'
        assert newapp.NewProj('whatever', "wrong-command").msg == 'foutief tweede argument (actie)*'
        assert newapp.NewProj('whatever', "undo").msg == 'project niet gevonden'
        assert newapp.NewProj('whatever', 'loaddata').msg == 'foute argumenten voor loaddata*'
        load_from = 'testdata.xml'
        assert newapp.NewProj('whatever', 'loaddata', load_from).msg == 'project niet gevonden'
        assert newapp.NewProj('whatever', 'loaddata', load_from, 'whatever').msg == (
                'foute argumenten voor loaddata*')
        assert newapp.NewProj('whatever', "copy", 'whatever').msg == 'teveel argumenten*'
        assert newapp.NewProj('whatever', "activate", 'whatever').msg == 'teveel argumenten*'
        assert newapp.NewProj('whatever', "undo", 'whatever').msg == 'teveel argumenten*'

    def test_activated_app(self):
        "test situations that produce no error messages"
        shutil.copyfile('apps.dat', 'apps.dat.o')
        with open('apps.dat', 'a') as f:
            f.write('X;apropos;apropos;bij de les blijf applicatie\n')
        test = newapp.NewProj('apropos', "all")
        assert test.msg == 'dit project is al geactiveerd'
        test = newapp.NewProj('apropos', "loaddata", "apropos.xml")
        assert test.msg is None
        assert (test.root, test.action, test.load_from, test.app) == ('apropos', 'loaddata',
                                                                      'apropos.xml', 'apropos')
        test = newapp.NewProj('apropos', "undo")
        assert test.msg is None
        assert (test.root, test.action, test.load_from, test.app) == ('apropos', 'undo', '',
                                                                      'apropos')
        os.remove('apps.dat')
        os.rename('apps.dat.o', 'apps.dat')

    def test_ok_activated_app(self):
        "test situations that produce no error messages"
        shutil.copyfile('apps.dat', 'apps.dat.o')
        with open('apps.dat', 'a') as f:
            f.write('_;printdir;printdir;directory afdrukken\n')
        test = newapp.NewProj('printdir', "undo")
        assert test.msg == 'dit project is nog niet geactiveerd'
        test = newapp.NewProj('printdir')
        assert test.msg is None
        assert (test.root, test.action, test.load_from, test.app) == ('printdir', 'all', '',
                                                                      'printdir')
        test = newapp.NewProj('printdir', "all")
        assert test.msg is None
        assert (test.root, test.action, test.load_from, test.app) == ('printdir', 'all', '',
                                                                      'printdir')
        test = newapp.NewProj('printdir', "copy")
        assert test.msg is None
        assert (test.root, test.action, test.load_from, test.app) == ('printdir', 'copy', '',
                                                                      'printdir')
        test = newapp.NewProj('printdir', "activate")
        assert test.msg is None
        assert (test.root, test.action, test.load_from, test.app) == ('printdir', 'activate', '',
                                                                      'printdir')
        test = newapp.NewProj('printdir', "loaddata", 'printdir.xml')
        assert test.msg is None
        assert (test.root, test.action, test.load_from, test.app) == ('printdir', 'loaddata',
                                                                      'printdir.xml', 'printdir')
        os.remove('apps.dat')
        os.rename('apps.dat.o', 'apps.dat')


class TestNewProj:
    """test NewProj class"""
    def test_str(self):
        """test string representation of class instantiated using certain args"""
        test = newapp.NewProj()
        assert str(test) == "newapp.NewProj('', '', '')"
        test = newapp.NewProj('x', 'y', 'z')
        assert str(test) == "newapp.NewProj('x', 'y', '')"
        test = newapp.NewProj('x', 'loaddata', 'z')
        assert str(test) == "newapp.NewProj('x', 'loaddata', 'z')"

    def _test_do_stuff(self):
        pass


class TestNewProjFunctions:
    where_proj = pathlib.Path('testproj')
    where_tpl = pathlib.Path('templates/testproj')

    def _test_do_copy(self):
        "test copy method of NewApp class"
        # setup
        shutil.copyfile('apps.dat', 'apps.dat.o')
        with open('apps.dat', 'a') as f:
            f.write('_;testproj;TestProj;test project\n')
        # call and check
        test = newapp.NewProj('testproj', 'copy')
        test.do_copy()
        # verwacht resultaat: gekopieerde ROOT_FILES (inhoud is gecontroleerd in copyover test
        # class) en gekopieerde TEMPLATE_FILES
        assert sorted([x.name for x in self.where_proj.iterdir()]) == sorted(newapp.ROOT_FILES)
        assert sorted([x.name for x in self.where_tpl.iterdir()]) == (
                         sorted([x + '.html' for x in newapp.TEMPLATE_FILES]))
        # teardown
        for path in self.where_proj.iterdir():
            path.unlink()
        self.where_proj.rmdir()
        for path in self.where_tpl.iterdir():
            path.unlink()
        self.where_tpl.rmdir()
        os.remove('apps.dat')
        os.rename('apps.dat.o', 'apps.dat')

    def _test_activate(self):
        "test activating the specified project(s)"
        # setup
        shutil.copyfile('apps.dat', 'apps.dat.o')
        with open('apps.dat', 'a') as f:
            f.write('_;testproj;TestProj;test project\n')
        # database backuppen
        shutil.copyfile('actiereg.db', 'actiereg.db.backup')
        # de eigenlijke test
        test = newapp.NewProj('testproj', "activate")
        test.activate()
        # verwacht resultaat:
        # bijgewerkt settings.py als gevolg van update_settings
        # bijgewerkt apps.dat als gevolg vam update.appreg
        # manage.py syncdb - database moet bepaalde tables bevatten o.b.v. aanpassingen
        #  die geactiveerd zouden moeten worden doordat de nieuwe app is toegevoegd aan settings.py
        # manage.py loaddata initial_data.json - tables moeten met bepaalde gegevens gevuld zijn
        # - auth tables moeten met bepaalde gevens gevuld zijn
        # check database: initial data was loaded, auth was built
        # teardown
        # teardown_testproj() - zit in tearDown methode
        # teardown_projdirs(root)
        for path in self.where_proj.iterdir():
            path.unlink()
        self.where_proj.rmdir()
        for path in self.where_tpl.iterdir():
            path.unlink()
        self.where_tpl.rmdir()
        # teardown_projdb() - database backup terugzetteni
        os.rename('actiereg.db.backup', 'actiereg.db')
        os.remove('apps.dat')
        os.rename('apps.dat.o', 'apps.dat')

    def _test_do_all(self):
        # setup
        shutil.copyfile('apps.dat', 'apps.dat.o')
        #teardown
        os.remove('apps.dat')
        os.rename('apps.dat.o', 'apps.dat')

    def _test_undo(self):
        # setup
        shutil.copyfile('apps.dat', 'apps.dat.o')
        #teardown
        os.remove('apps.dat')
        os.rename('apps.dat.o', 'apps.dat')

    def _loaddata(self):
        # setup
        shutil.copyfile('apps.dat', 'apps.dat.o')
        #teardown
        os.remove('apps.dat')
        os.rename('apps.dat.o', 'apps.dat')


class TestNewProjHelpers:
    def _test_update_settings(self):
        """test update_settings (doet het bijwerken van settings.py in de root
        """
        # bestaande backup veiligstellen om straks terug te kunnen zetten
        sett = newapp.BASE / "settings.py"
        settcopy = newapp.BASE / "settings.py~"
        settold = newapp.BASE / "settings.py~.backup"
        if settcopy.exists():
            settcopy.replace(settold)
        for action, seq in (("activate", '0'), ("undo", '1')):
            old = get_contents_for_compare(sett)
            # de test
            test = newapp.NewProj('testproj', action)
            test.update_settings()
            # de analyse
            new = get_contents_for_compare(sett)
            difflines = difflib.ndiff(old, new)
            realdifflines = [x for x in difflines if x.startswith('-') or x.startswith('+')]
            origoutfile = pathlib.Path('settings.py.diff.{}'.format(seq))
            if origoutfile.exists():
                origdifflines = origoutfile.read_text()
            else:
                origdifflines = realdifflines
                origoutfile.write_text(''.join(origdifflines))
            assert realdifflines == origdifflines
        # teardown
        if settold.exists():
            settold.replace(settcopy)
        else:
            settcopy.unlink()
        for seq in ['0', '1']:
            pathlib.Path('settings.py.diff.{}'.format(seq)).unlink()

    def _test_update_urlconf(self):
        pass

    def _test_update_appreg(self):
        """update_appreg doet het bijwerken van apps.dat
        """
        sett = newapp.BASE / "apps.dat"
        settorig = newapp.BASE / "apps.dat.backup"
        settcopy = newapp.BASE / "apps.dat~"
        settold = newapp.BASE / "apps.dat~.backup"
        settorig.write_text(sett.read_text())
        if settcopy.exists():
            settcopy.replace(settold)
        with open('apps.dat', 'a') as f:
            f.write('_;testproj;TestProj;test project\n')
        for action, seq in (("activate", '0'), ("undo", '1')):
            old = get_contents_for_compare(sett)
            # de test
            test = newapp.NewProj('testproj', action)
            test.update_appreg()
            # de analyse
            new = get_contents_for_compare(sett)
            difflines = difflib.ndiff(old, new)
            realdifflines = [x for x in difflines if x.startswith('-') or x.startswith('+')]
            origoutfile = pathlib.Path('apps.dat.diff.{}'.format(seq))
            if origoutfile.exists():
                origdifflines = origoutfile.read_text()
            else:
                origdifflines = realdifflines
                origoutfile.write_text(''.join(origdifflines))
            assert realdifflines == origdifflines
        # teardown
        settorig.replace(sett)
        if settold.exists():
            settold.replace(settcopy)
        else:
            settcopy.unlink()
        for seq in ['0', '1']:
            pathlib.Path('apps.dat.diff.{}'.format(seq)).unlink()


def _test_allnew(monkeypatch, capsys):
    pass
