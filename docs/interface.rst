.. role:: raw-html(raw)
   :format: html

.. |plus| replace:: :raw-html:`<span class="fa fa-plus-square"></span>`
.. |search| replace:: :raw-html:`<span class="fa fa-search"></span>`
.. |eye| replace:: :raw-html:`<span class="fa fa-eye"></span>`
.. |bars| replace:: :raw-html:`<span class="fa fa-bars"></span>`
.. |lock| replace:: :raw-html:`<span class="fa fa-lock"></span>`
.. |unlock| replace:: :raw-html:`<span class="fa fa-unlock-alt"></span>`
.. |info| replace:: :raw-html:`<span class="fa fa-info-circle"></span>`
.. |next| replace:: :raw-html:`<span class="fa fa-chevron-circle-right"></span>`
.. |previous| replace:: :raw-html:`<span class="fa fa-chevron-circle-left"></span>`
.. |eraser| replace:: :raw-html:`<span class="fa fa-eraser"></span>`
.. |circle| replace:: :raw-html:`<span class="fa fa-circle"></span>`


Interface
---------

Editor
~~~~~~

.. figure:: _static/screenshots/editor_00.jpg
   :width: 500px
   :align: center
   :alt: Editor

**Menubar**:

.. figure:: _static/screenshots/editor_menubar.jpg
   :align: center
   :alt: Editor

- 'New title' : Show/Configure presentation title (`see <#edit-presentation-title>`_)
- |plus| : Add slide to presentation. ( `see <#add-new-slide>`_)
- |search| : Switch to `search <#search>`_.
- |eye| : Switch to `viewer <#viewer>`_.
- |bars| : File Menu (New, Open, Save, Save as..., Quit)


Edit presentation title
^^^^^^^^^^^^^^^^^^^^^^^

.. _edit_title-label:

- Click on 'New title' to show the edit dialog, press 'Enter' to validate.

.. figure:: _static/screenshots/editor_01.jpg
   :width: 500px
   :align: center
   :alt: Edit title

Add new slide
^^^^^^^^^^^^^

To add new slide :

-  Left click on |plus| icon.
-  The file explorer appear : select the file you want to add as a slide by double clicking on it.

.. figure:: _static/screenshots/editor_03.jpg
   :width: 500px
   :align: center
   :alt: Adding slide

- The slide is added to the presentation view and a dialog appear.

.. figure:: _static/screenshots/editor_02.jpg
   :width: 500px
   :align: center
   :alt: Adding slide

- Enter slide informations and validate by pressing `Enter`.

Edit slide
^^^^^^^^^^

- Double click on the slide to show the edit dialog.

Show slide informations
^^^^^^^^^^^^^^^^^^^^^^^^

- Click on |info| to show/hide slide informations.

Remove slide
^^^^^^^^^^^^

Left click on slide, drag it on a corner of the screen and drop it, it should be removed from presentation.

Re-order slides
^^^^^^^^^^^^^^^
- Drag-and-drop the slide where you want it to be.
- Order is from top left to bottom right.

Search
~~~~~~

.. figure:: _static/screenshots/search_01.jpg
   :width: 500px
   :align: center
   :alt: Search

**Menubar**

.. figure:: _static/screenshots/search_menubar.jpg
   :width: 500px
   :align: center
   :alt: Search menu bar

- Click on app icon on the left : go back to editor.
- Click on dropdown menu on the right : select search engine.

Search for a picture
^^^^^^^^^^^^^^^^^^^^

- Type your request in the text input box under the menubar and validate by pressing `Enter`

.. figure:: _static/screenshots/search_03.jpg
   :width: 500px
   :align: center
   :alt: Search

- |next| : show next page of results.
- |previous| : show previous page of results.

Add picture as slide to presentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Click on the picture you want to add to make appear a dialog showing a slightly better image (depending on the source).

.. figure:: _static/screenshots/search_04.jpg
   :width: 500px
   :align: center
   :alt: Search

- Click on `Add to presentation` to begin download.

.. note:: Hadaly always tries to download the best image quality.

.. figure:: _static/screenshots/search_05.jpg
   :width: 500px
   :align: center
   :alt: Search

- Once download is finished, slide is automatically added to presentation with metadata extracted from the source if available.

.. figure:: _static/screenshots/search_06.jpg
   :width: 500px
   :align: center
   :alt: Search

Viewer
~~~~~~

.. figure:: _static/screenshots/viewer_01.jpg
   :width: 500px
   :align: center
   :alt: Viewer

Move slide:
^^^^^^^^^^^

Left click on slide and drag it around the screen.

Zoom in or out:
^^^^^^^^^^^^^^^

-  Zoom with mouse wheel.
-  Or use two finger touch emulation with right click (a red dot
   appear):

.. figure:: _static/screenshots/viewer_02.jpg
   :width: 500px
   :align: center
   :alt: Viewer zoom

-  Maintain left click and drag cursor to zoom in or out. If a portion of
   the slide is out of sight, a small thumbnail will appear at the
   bottom left :

.. figure::  _static/screenshots/viewer_03.jpg
   :width: 500px
   :align: center
   :alt: Thumbnail

Switch to editor:
^^^^^^^^^^^^^^^^^

Double click on top left corner of the screen.

Switch to next or previous slide:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Left click and swipe left or right.

Switch to 'x' slide:
^^^^^^^^^^^^^^^^^^^^

Double click on bottom right corner of the screen and select slide:

.. figure:: _static/screenshots/viewer_04.jpg
   :width: 500px
   :align: center
   :alt: Viewer zoom

Compare current slide with another one:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  Double click on center of the screen and select slide:

.. figure:: _static/screenshots/viewer_05.jpg
   :width: 500px
   :align: center
   :alt: Viewer zoom

-  Compare mode in action:

.. figure:: _static/screenshots/viewer_06.jpg
   :width: 500px
   :align: center
   :alt: Viewer zoom

-  Double click on center of the screen to remove compared slide.

Draw on slide:
^^^^^^^^^^^^^^

.. note:: When drawing is activated it is not possible to move the slide. You can only scale it with mouse wheel.

- Click on |unlock| icon in bottom left corner.
- Icon should change to |lock| and toolbar should appear.

.. figure:: _static/screenshots/viewer_08.jpg
   :width: 500px
   :align: center
   :alt: Viewer toolbar

- You can now draw on the slide.

.. figure:: _static/screenshots/viewer_09.jpg
   :width: 500px
   :align: center
   :alt: Viewer toolbar

- To delete drawings, click on |eraser|.

Change tool color:
^^^^^^^^^^^^^^^^^^

- Click on |circle| to show the color picker

.. figure:: _static/screenshots/viewer_10.jpg
   :width: 500px
   :align: center
   :alt: Viewer toolbar

- Select color by clicking on the color wheel or by entering RGBA informations.
- Click out of the dialog to close it.

Increase/Decrease tool thickness
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Move the slider of the toolbar to the right to increase line size (Mouse wheel also works).

Options
~~~~~~~

'F1' : Show options panel.

.. figure:: _static/screenshots/options_01.jpg
   :width: 500px
   :align: center
   :alt: Viewer zoom


Shortcuts
~~~~~~~~~

- ``Ctrl-e`` : Enter drawing mode.
- ``Ctrl-d`` : Delete drawings.
- ``Left`` : Go to previous slide.
- ``Right`` : Go to next slide.
