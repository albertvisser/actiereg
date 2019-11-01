"""unittests for newapp mdule
"""
import unittest
import os
import shutil
import pathlib
import difflib
import actiereg.newapp as newapp


def get_contents_for_compare(path):
    "read contents of specified file"
    return [x + '\n' for x in path.read_text().split('\n')]


class TestCopyOver(unittest.TestCase):
    """test copyover varianten"""

    def setUp(self):
        self.where = newapp.BASE / 'test'
        self.where.mkdir()

    def test_using_none(self):
        "using None as one of the three arguments"
        with self.assertRaises(TypeError):
            newapp.copyover(None, 'xxx', 'yyy')
        with self.assertRaises(TypeError):
            newapp.copyover('xxx', None, 'yyy')
        with self.assertRaises(FileNotFoundError):
            newapp.copyover('xxx', 'yyy', None)

    def test_using_empty_string(self):
        "using empty string as one of the three arguments"
        with self.assertRaises(FileNotFoundError):
            newapp.copyover('', 'xxx', 'yyy')
        with self.assertRaises(IsADirectoryError):
            newapp.copyover('xxx', '', 'yyy')
        with self.assertRaises(FileNotFoundError):
            newapp.copyover('xxx', 'yyy', '')

    def test_wrong_filename(self):
        "using filename not in list"
        with self.assertRaises(FileNotFoundError):
            newapp.copyover('test', 'snork', 'gargl')

    def test_project_filenames(self):
        "trying out all listed filenames"
        for name in newapp.ROOT_FILES:
            newapp.copyover('test', name, 'gargl')
            path = self.where / name
            oldpath = newapp.BASE / '_basic' / name
            self.assertEqual(path.exists(), True, 'file not copied')
            if name in newapp.SYMLINK:
                # test of er een symlink gemaakt is
                self.assertEqual(path.is_symlink(), True, 'path is not a symlink')
                self.assertEqual(os.readlink(str(path)), str(oldpath),
                                 'path points to the wrong file')
            else:
                # test of file gekopieerd is inclusief correcte edits
                data = path.read_text().replace('_basic', name)
                data = data.replace('basic', name).replace('demo', 'gargl')
                self.assertEqual(path.read_text(), data, 'contents not correctly copied')

    def tearDown(self):
        for path in self.where.iterdir():
            path.unlink()
        self.where.rmdir()


class TestBackup(unittest.TestCase):
    "test backup functie"

    def setUp(self):
        self.path = pathlib.Path('kloenk')

    def test_using_none(self):
        "test for filename is None"
        with self.assertRaises(TypeError):
            newapp.backup(pathlib.Path(None))
        self.assertEqual(os.path.exists('None~'), False)

    def test_empty_filename(self):
        "test for empty filename"
        with self.assertRaises(OSError):
            newapp.backup(pathlib.Path(''))
        self.assertEqual(os.path.exists('~'), False)

    def test_nonexistant_file(self):
        "test for nonexistant file"
        if self.path.exists():
            self.path.unlink()
        with self.assertRaises(FileNotFoundError):
            newapp.backup(self.path)

    def test_backup(self):
        "test for existing file"
        if not self.path.exists():
            self.path.touch()
        newapp.backup(self.path)
        self.assertEqual(os.path.exists('kloenk'), False)
        self.assertEqual(os.path.exists('kloenk~'), True)


class TestNewProj(unittest.TestCase):
    """test NewProj class"""
    def setUp(self):
        shutil.copyfile('apps.dat', 'apps.dat.o')
        self.where_proj = pathlib.Path('testproj')
        self.where_tpl = pathlib.Path('templates/testproj')

    def test_str(self):
        """test string representation of class instantiated using certain args"""
        test = newapp.NewProj()
        self.assertEqual(str(test), "newapp.NewProj('', '', '')")
        test = newapp.NewProj('x', 'y', 'z')
        self.assertEqual(str(test), "newapp.NewProj('x', 'y', '')")
        test = newapp.NewProj('x', 'loaddata', 'z')
        self.assertEqual(str(test), "newapp.NewProj('x', 'loaddata', 'z')")

    def test_parse_args_messages(self):
        "test situations that produce error messages"
        test = newapp.NewProj('whatever')
        self.assertEqual(test.msg, 'project niet gevonden')
        test = newapp.NewProj('whatever', "wrong-command")
        self.assertEqual(test.msg, 'foutief tweede argument (actie)*')
        test = newapp.NewProj('whatever', "undo")
        self.assertEqual(test.msg, 'project niet gevonden')
        test = newapp.NewProj('whatever', 'loaddata')
        self.assertEqual(test.msg, 'foute argumenten voor loaddata*')
        load_from = 'testdata.xml'
        test = newapp.NewProj('whatever', 'loaddata', load_from)
        self.assertEqual(test.msg, 'project niet gevonden')
        test = newapp.NewProj('whatever', 'loaddata', load_from, 'whatever')
        self.assertEqual(test.msg, 'foute argumenten voor loaddata*')
        test = newapp.NewProj('whatever', "copy", 'whatever')
        self.assertEqual(test.msg, 'teveel argumenten*')
        test = newapp.NewProj('whatever', "activate", 'whatever')
        self.assertEqual(test.msg, 'teveel argumenten*')
        test = newapp.NewProj('whatever', "undo", 'whatever')
        self.assertEqual(test.msg, 'teveel argumenten*')

    def test_parse_args_activated_app(self):
        "test situations that produce no error messages"
        with open('apps.dat', 'a') as f:
            f.write('X;apropos;apropos;bij de les blijf applicatie\n')
        test = newapp.NewProj('apropos', "all")
        self.assertEqual(test.msg, 'dit project is al geactiveerd')
        test = newapp.NewProj('apropos', "loaddata", "apropos.xml")
        self.assertIsNone(test.msg)
        self.assertEqual((test.root, test.action, test.load_from, test.app),
                         ('apropos', 'loaddata', 'apropos.xml', 'apropos'))
        test = newapp.NewProj('apropos', "undo")
        self.assertIsNone(test.msg)
        self.assertEqual((test.root, test.action, test.load_from, test.app),
                         ('apropos', 'undo', '', 'apropos'))

    def test_parse_args_ok_activated_app(self):
        "test situations that produce no error messages"
        with open('apps.dat', 'a') as f:
            f.write('_;printdir;printdir;directory afdrukken\n')
        test = newapp.NewProj('printdir', "undo")
        self.assertEqual(test.msg, 'dit project is nog niet geactiveerd')
        test = newapp.NewProj('printdir')
        self.assertIsNone(test.msg)
        self.assertEqual((test.root, test.action, test.load_from, test.app),
                         ('printdir', 'all', '', 'printdir'))
        test = newapp.NewProj('printdir', "all")
        self.assertIsNone(test.msg)
        self.assertEqual((test.root, test.action, test.load_from, test.app),
                         ('printdir', 'all', '', 'printdir'))
        test = newapp.NewProj('printdir', "copy")
        self.assertIsNone(test.msg)
        self.assertEqual((test.root, test.action, test.load_from, test.app),
                         ('printdir', 'copy', '', 'printdir'))
        test = newapp.NewProj('printdir', "activate")
        self.assertIsNone(test.msg)
        self.assertEqual((test.root, test.action, test.load_from, test.app),
                         ('printdir', 'activate', '', 'printdir'))
        test = newapp.NewProj('printdir', "loaddata", 'printdir.xml')
        self.assertIsNone(test.msg)
        self.assertEqual((test.root, test.action, test.load_from, test.app),
                         ('printdir', 'loaddata', 'printdir.xml', 'printdir'))

    def test_do_copy(self):
        "test copy method of NewApp class"
        # setup
        with open('apps.dat', 'a') as f:
            f.write('_;testproj;TestProj;test project\n')
        # call and check
        test = newapp.NewProj('testproj', 'copy')
        test.do_copy()
        # verwacht resultaat: gekopieerde ROOT_FILES (inhoud is gecontroleerd in copyover test
        # class) en gekopieerde TEMPLATE_FILES
        self.assertEqual(sorted([x.name for x in self.where_proj.iterdir()]),
                         sorted(newapp.ROOT_FILES))
        self.assertEqual(sorted([x.name for x in self.where_tpl.iterdir()]),
                         sorted([x + '.html' for x in newapp.TEMPLATE_FILES]))
        # teardown
        for path in self.where_proj.iterdir():
            path.unlink()
        self.where_proj.rmdir()
        for path in self.where_tpl.iterdir():
            path.unlink()
        self.where_tpl.rmdir()

    def test_update_settings(self):
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
            self.assertEqual(realdifflines, origdifflines)
        # teardown
        if settold.exists():
            settold.replace(settcopy)
        else:
            settcopy.unlink()
        for seq in ['0', '1']:
            pathlib.Path('settings.py.diff.{}'.format(seq)).unlink()

    def test_update_appreg(self):
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
            self.assertEqual(realdifflines, origdifflines)
        # teardown
        settorig.replace(sett)
        if settold.exists():
            settold.replace(settcopy)
        else:
            settcopy.unlink()
        for seq in ['0', '1']:
            pathlib.Path('apps.dat.diff.{}'.format(seq)).unlink()

    def test_activate(self):
        "test activating the specified project(s)"
        # setup
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

    ## def test_do_all(self):
        ## ""

    ## def test_undo(self):
        ## ""

    def tearDown(self):
        os.remove('apps.dat')
        os.rename('apps.dat.o', 'apps.dat')


## if __name__ == '__main__':
    ## unittest.main()
