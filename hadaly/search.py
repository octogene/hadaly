# -*- coding: utf-8 -*-
from lxml import html
from urllib.parse import urlparse, parse_qs
from urllib.request import urlopen

from kivy.core.window import Window
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.properties import DictProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen

from .editor import Slide


class SearchScreen(Screen):
    def on_enter(self, *args):
        self.box.term.focus = True


class SearchBox(BoxLayout):
    app = ObjectProperty(None)
    current_page = ObjectProperty(1)
    total_pages = ObjectProperty(None)
    status = ObjectProperty('')

    def search(self, term, provider):
        Logger.debug('Search: requesting {term} from {provider}'.format(term=term,
                                                                        provider=provider))
        self.grid.clear_widgets()
        providers = {'MetMuseum': 'www.metmuseum.org',
                     'Getty OCI': 'search.getty.edu'}
        if not term:
            popup = Popup(title=_('Error'), size_hint=(0.45, 0.2))
            popup.add_widget(Label(text=_('Please enter a search term.')))
            popup.open()
            return
        elif provider == 'Flickr':
            results = self.app.search_flickr(term)
            for photo in results['photos']['photo']:
                photo['thumb'] = self.app.get_flickr_url(photo, 't')
                photo['artist'] = photo['owner']
                photo['year'] = 'None'
                Logger.debug('Search (Flickr): Loading {url}'.format(url=photo['thumb']))
                image = ItemButton(photo=photo, source=photo['thumb'], keep_ratio=True, size_hint=(None, None))
                self.grid.add_widget(image)
        elif provider == _('Select a search engine'):
            popup = Popup(title=_('Error'), size_hint=(0.45, 0.2))
            popup.add_widget(Label(text=_('Please select a search engine.')))
            popup.open()
        elif provider == 'MetMuseum':
            self.app.search_term(term, providers[provider], self.current_page)
        elif provider == 'Getty OCI':
            self.app.search_term(term, providers[provider], self.current_page)

    def search_next(self, text, provider):
        if self.current_page < int(self.total_pages):
            self.current_page += 1
            self.search(text, provider)

    def search_previous(self, text, provider):
        if self.current_page > 1:
            self.current_page -= 1
            self.search(text, provider)


class ItemButton(ButtonBehavior, AsyncImage):
    photo = DictProperty(None)

    def on_press(self):
        if 'metmuseum.org' in self.photo['thumb']:
            src = self.photo['thumb'].replace('web-thumb', 'web-large')
            popup = SearchItemInfo(photo=self.photo, thumbnail=src, provider='MET')
            popup.open()
        elif 'getty.edu' in self.photo['thumb']:
            popup = SearchItemInfo(photo=self.photo, thumbnail=self.photo['thumb'], provider='Getty')
            popup.open()
        else:
            src = self.photo['thumb'].replace('t.jpg', 'm.jpg')
            popup = SearchItemInfo(photo=self.photo, thumbnail=src, provider='Flickr')
            popup.open()


class SearchItemInfo(Popup):
    photo = DictProperty(None)
    thumbnail = StringProperty(None)
    provider = StringProperty(None)

    # TODO: Better async download of image and thumb creation.
    def add_to_presentation(self):
        """Download high-res image and add slide to presentation.

        """
        app = ObjectProperty(None)

        slide = Slide(img_src=self.photo['thumb'],
                      thumb_src=self.photo['thumb'],
                      artist=self.photo['artist'],
                      title=self.photo['title'],
                      year=self.photo['year'])

        if self.provider == 'MET':
            # Check if high-res is available.
            url = self.photo['thumb'].replace('mobile-large', 'original')
            req = urlopen(url)
            if req.getcode() == 404:
                Logger.debug('Search: High-res image not available.')
                self.app.show_popup(_('Error'), _('High-res image not available, downloading inferior quality.'))
                self.app.download_img(self.thumbnail, slide)
                self.app.add_slide(slide)
            else:
                self.app.download_img(url, slide)
                self.app.add_slide(slide)

        elif self.provider == 'Getty':

            req = urlopen(self.photo['obj_link'])
            tree = html.parse(req)
            img_link = tree.xpath('//a[@id="download-open-content"]/@href')
            if img_link:
                link = urlparse(img_link[0])
                url = parse_qs(link.query)['dlimgurl'][0]
            else:
                url = self.photo['thumb']
            slide.img_src = url
            self.app.download_img(url, slide)
            self.app.add_slide(slide)

        elif self.provider == 'Flickr':
            # thumb_filename = basename(self.photo['thumb'])
            # thumb = splitext(thumb_filename)
            # url = ''.join((thumb[0][:-1], 'o', thumb[1]))
            url = app.get_flickr_url(self.photo, 'o')
            self.app.download_img(url, slide)
            self.app.add_slide(slide)
