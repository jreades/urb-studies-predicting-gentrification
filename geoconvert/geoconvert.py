from bs4 import BeautifulSoup
import requests
import urllib.request
import six
import re
import os

class form_parser(object):
    """
    Simple class to parse forms of the style used by MIMAS.
    """

    def u2str(self, u):
        if isinstance(u, str):
            return u
        else:
            return unicode.strip(u).encode('ascii','ignore')

    def get_parent_text(self, t):
        ptext = t.parent.text
        if self.u2str(ptext) is '':
            if t.parent.name=='td':
                #table = t.findParents('table')[0]
                tr = t.findParents('tr')[0]
                #print(tr)
                cols = []
                for td in tr.find_all('td'):
                    cols.append(self.u2str(td.text))

                if len(cols)==1:
                    ptext = cols[0]
                elif len(cols)==2:
                    ptext = " -> ".join(cols)
                elif len(cols)==3:
                    ptext = " -> ".join([cols[0],cols[1]])
                elif len(cols)==4:
                    ptext = " -> ".join([cols[1],cols[3]])
                elif len(cols)==5:
                    ptext = " -> ".join([cols[1],cols[4]])
                else:
                    ptext = ", ".join(cols)
            else:
                ptext = 'fail'
        return self.u2str(ptext)

    def find_radios(self, f):
        radios = f.find_all('input', attrs={'type':'radio'})
        groups = set()
        for r in radios:
            groups.add(r.get('name'))
        return list(groups)

    def parse_radios(self, f, i):
        radios = f.find_all('input', attrs={'type':'radio','name':i})

        opts = {}
        for r in radios:

            #print("Radio: " + str(r))
            #print(r.attrs)

            if r.get('id') is not None:
                choice = self.u2str(r.get('id'))
            elif not self.get_parent_text(r).isspace():
                choice = self.get_parent_text(r)
            else:
                choice = r.attrs['value']

            opts[choice] = r.attrs['value']
        return opts

    def find_selects(self, f):
        selects = f.find_all('select')
        return selects

    def parse_select(self, s):
        choices = {}
        sid      = s.attrs['name']
        soptions = {}
        for o in s.find_all('option'):
            soptions[self.u2str(o.text)] = o.get('value')
        return sid, soptions

    def find_hidden(self, f):
        hidden = f.find_all('input', attrs={'type':'hidden'})
        return hidden

    def parse_hidden(self, h):
        #print(h)
        return h.attrs['name'], h.attrs['value']

    def __init__(self):
        return None

    def parse(self, f):
        params = {}
        params['action'] = f.get('action') # We'll always want this to know what to do next
        params['hidden'] = {}              # We don't want to mess about with these

        # Possible form name and it
        #if 'name' in f.attrs:
        #    fname = f.attrs['name']
        #    fid   = f.attrs['id']
        #    if fname is not None:
        #        params['form'] = [f.attrs['name'], f.attrs['id']]

        # Any values for the submit button
        sval = f.find('input', attrs={'type':'submit'})
        if sval:
            sid    = sval.get('name')
            svalue = sval.get('value')
            if sid is not None:
                params['submit'] = [
                    sid,
                    svalue
                ]

        # Parse radio buttons into groups
        for i in self.find_radios(f):
            params[i] = self.parse_radios(f, i)

        # Parse selects into groups
        for j in self.find_selects(f):
            (n, v) = self.parse_select(j)
            params[n] = v

        # Parse hidden form elements into key/value pairs
        for k in self.find_hidden(f):
            (n, v) = self.parse_hidden(k)
            params['hidden'][n] = v

        return params


class geoconvert(object):
    """
    Simple class to convert LSOA 2001 to 2011. May
    work for other geographies but not tested.
    """
    site      = 'http://geoconvert.mimas.ac.uk/application/'
    startpage = 'step1credentials.cfm'

    def __init__(self):

        # We need to keep the cookies in a session
        self.session = requests.Session()
        self.parser  = form_parser()
        self.soups   = []

        # Request initial form
        self.get(page=self.startpage)

        print("Session started...")
        print("\tToken: " + str(self.session.cookies['CFTOKEN']))

        return None

    def post(self, page=None, payload=None, files=None):
        if page is None:
            print("Warning: no page parameter!")
        else:
            if payload is not None and files is not None:
                #print("Option 1: payload and files")
                self.soups.append(
                    BeautifulSoup(self.session.post(self.site + page, data=payload, files=files).text, 'lxml')
                )
            elif payload is not None and files is None:
                #print("Option 2: payload, no files")
                self.soups.append(
                    BeautifulSoup(self.session.post(self.site + page, data=payload).text, 'lxml')
                )
            else:
                #print("Option 3: no payload or files")
                self.soups.append(
                    BeautifulSoup(self.session.post(self.site + page).text, 'lxml')
                )

    def get(self, page=None):
        if page is None:
            print("Warning: no page parameter!")
        else:
            self.soups.append(
                BeautifulSoup(self.session.get(self.site + page).text, 'lxml')
            )

    def auto_2001_to_2011(self, ufile=None):
        self.step1()
        self.step2()
        self.step3()
        self.step4()
        self.step5()
        self.step6(ufile)
        self.step7()
        self.get_files()

    def step1(self, action={'functionbutton':'convert'}):

        # Find and parse the form
        pf = self.parser.parse(self.soups[-1].find('form'))

        # Create params for next call
        payload  = self.create_payload(pf, action)

        self.post(page=pf['action'], payload=payload)

        print("Conversion specified...")

    def step2(self, action={'sourcetype':'lower'}):

        # Find and parse the form
        pf = self.parser.parse(self.soups[-1].find('form'))

        # Create params for next call
        payload = self.create_payload(pf, action)

        # Request it
        self.post(page=pf['action'], payload=payload)

        print("LSOA source specified...")

    def step3(self, action={'targettype':'lower'}):

        # Find and parse the form
        pf = self.parser.parse(self.soups[-1].find('form'))

        # Create params for next call
        payload = self.create_payload(pf, action)

        # Request it
        self.post(page=pf['action'], payload=payload)

        print("LSOA target specified...")

    def step4(self, action={'find_lut':'LUT_LSOADZ0115jul_LSOADZ1115jul'}):

        # Find and parse the form
        pf = self.parser.parse(self.soups[-1].find('form'))

        #print(pf)
        #print(self.soups[-1].prettify())

        # Create params for next call
        payload = self.create_payload(pf, action)

        # Request it
        self.post(page=pf['action'], payload=payload)

        print("2001 to 2011 LSOA conversion specified...")

    def step5(self):

        # Find and parse the form
        pf = self.parser.parse(self.soups[-1].find('form'))

        # Create params for next call
        payload = self.create_payload(pf)

        # Request it
        self.post(page=pf['action'], payload=payload)

        print("Ready to submit data...")

    def step6(self, fp, action={'header':'yes', 'delimiter':'comma'}):

        # Find and parse the form
        pf = self.parser.parse(self.soups[-1].find('form'))

        # Create params for next call
        payload = self.create_payload(pf, action)

        # Useful output
        self.fn  = os.path.split(fp)[1]

        files    = {'useruploadfile': open(fp,'rb')}
        self.post(page=pf['action'], payload=payload, files=files)

        print("File '" + self.fn + "' uploaded for conversion")

    def step7(self):

        # Find and parse the form
        pf = self.parser.parse(self.soups[-1].find('form'))

        # Create params for next call
        payload = self.create_payload(pf)

        # Request it
        self.post(page=pf['action'], payload=payload)

        print("Annoying extra step to access converted files complete.")

    def get_files(self):

        dlinks = self.soups[-1].find_all('a', attrs={'class':'gresults'})
        partfn = re.sub(".csv","",self.fn)
        for l in dlinks:

            rpath = self.parser.u2str(l.get('href')).split("\\")
            rname = re.sub("\d+_", "", rpath[-1])

            urllib.request.urlretrieve(self.site + "/".join(rpath), '-'.join([partfn,rname]))
            print("Downloading: " + '-'.join([partfn,rname]))

    # Create a requests payload
    def create_payload(self, p, selections={}):
        payload = {}
        if 'form' in p:
            payload[p['form'][0]] = p['form'][1]

        if 'submit' in p:
            payload[p['submit'][0]] = p['submit'][1]

        for k, v in p['hidden'].items():
            payload[k] = v

        for s, v in selections.items():

            #print(s + " -> " + v)
            #print("\t" + str(p[s].keys()))
            #print([p[s][x] for x in p[s].keys() if v.lower() in x.lower()][0])
            payload[s] = [p[s][x] for x in p[s].keys() if v.lower() in x.lower()][0]

        return payload
