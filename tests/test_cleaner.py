import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from arabic_csv_cleaner import clean_csv, normalize_cell

class CleanerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'input.csv'
        self.dest = self.root / 'output.csv'
    def put(self, text, encoding='utf-8'):
        self.source.write_text(text, encoding=encoding)
    def rows(self):
        with self.dest.open(encoding='utf-8-sig', newline='') as handle:
            return list(csv.reader(handle))
    def test_digits_and_identity(self):
        self.assertEqual(normalize_cell(' ٠٠١۲۳ '), '00123')
        self.assertEqual(normalize_cell('أحمد  علي ١٬٢٣٤٫٥'), 'أحمد  علي 1٬234٫5')
    def test_duplicates_opt_in(self):
        self.put('كود,كمية\n٠٠١,١٢\n۰۰۱,۱۲\n')
        report=clean_csv(self.source,self.dest)
        self.assertEqual(len(self.rows()),3)
        self.assertEqual(report['duplicate_rows'],1)
        self.assertEqual(report['removed_rows'],0)
    def test_deduplicate_and_bom(self):
        self.put(' كود ,كمية\n٠٠١,١٢\n۰۰۱,۱۲\n\n٠٠٢,٥\n')
        report=clean_csv(self.source,self.dest,deduplicate=True)
        self.assertEqual(self.rows(),[['كود','كمية'],['001','12'],['002','5']])
        self.assertEqual((report['input_rows'],report['output_rows'],report['blank_rows']),(3,2,1))
        self.assertTrue(self.dest.read_bytes().startswith(b'\xef\xbb\xbf'))
    def test_invalid_width_leaves_no_output(self):
        self.put('a,b\n1,2\n3\n')
        with self.assertRaises(ValueError): clean_csv(self.source,self.dest)
        self.assertFalse(self.dest.exists())
    def test_duplicate_normalized_headers(self):
        self.put(' رقم ,رقم\n1,2\n')
        with self.assertRaises(ValueError): clean_csv(self.source,self.dest)
    def test_empty_headers_and_files(self):
        for content in ['', 'a,\n1,2\n']:
            with self.subTest(content=content):
                self.put(content)
                with self.assertRaises(ValueError): clean_csv(self.source,self.dest)
    def test_existing_destination_unchanged(self):
        self.put('a\n1\n');self.dest.write_text('KEEP')
        with self.assertRaises(FileExistsError): clean_csv(self.source,self.dest)
        self.assertEqual(self.dest.read_text(),'KEEP')
    def test_same_path_unchanged(self):
        self.put('a\n١\n'); original=self.source.read_bytes()
        with self.assertRaises(ValueError): clean_csv(self.source,self.source)
        self.assertEqual(original,self.source.read_bytes())
    def test_formula_escape_includes_header(self):
        self.put(' =name,value\n @SUM(1),-١\n')
        report=clean_csv(self.source,self.dest,safe_excel=True)
        self.assertEqual(self.rows(),[["'=name","value"],["'@SUM(1)","'-1"]])
        self.assertEqual(report['formula_cells_escaped'],3)
    def test_legacy_encoding_and_delimiter(self):
        self.put('اسم;عدد\nكشاف;5\n',encoding='cp1256')
        clean_csv(self.source,self.dest,encoding='cp1256',delimiter=';')
        self.assertIn('كشاف;5',self.dest.read_text(encoding='utf-8-sig'))
    def test_quoted_multiline(self):
        self.put('a,b\n"مرحبا\nبك","١,٢"\n')
        clean_csv(self.source,self.dest)
        self.assertEqual(self.rows()[1],['مرحبا\nبك','1,2'])
    def test_malformed_quotes(self):
        self.put('a\n"unclosed\n')
        with self.assertRaises(csv.Error): clean_csv(self.source,self.dest)
        self.assertFalse(self.dest.exists())
    def test_cli_report(self):
        self.put('كود\n٠٠١\n')
        result=subprocess.run([sys.executable,'-m','arabic_csv_cleaner',str(self.source),str(self.dest)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)['output_rows'],1)
    def test_cli_failure(self):
        self.put('a,b\n1\n')
        result=subprocess.run([sys.executable,'-m','arabic_csv_cleaner',str(self.source),str(self.dest)],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertIn('Error:',result.stderr)

if __name__=='__main__': unittest.main()
