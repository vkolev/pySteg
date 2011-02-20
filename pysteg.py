#!/usr/bin/env python2.6
#-*- encoding: utf-8 -*-


import os
import sys
import pygtk
pygtk.require('2.0')
import gtk

import vte

from configobj import ConfigObj

try:
    import gtkmozembed
except:
    print "You dont'have python-webkitgtk installed!"

basepath = os.path.abspath(os.path.dirname(sys.argv[0]))

builder = gtk.Builder()
builder.add_from_file('%s/data/main.ui' % basepath)
config = ConfigObj("%s/data/pySteg.conf" % basepath)
# Check if steghide is installed
if os.path.isfile("/usr/bin/steghide"):
    pass
else:
    print "Steghide is not installed!"
    sys.exit()

#print config["algtypes"]['algoritm']


class PySteg:

    def on_window_destroy(self, widget, data=None):
        gtk.main_quit()

    def embed(self, button):
        # Define the Cover file
        covFile = self.covfile.get_filename() 
        if covFile == None:
            self.show_error("You have to select a <b>Cover file</b>",
                           "Select cover file")
            return 0
        else:
            covFile = ' -cf "' + covFile + '"'
        # Define the Embed file
        embedFile = self.embedfile.get_filename()
        if embedFile == None:
            self.show_error("You have to select an <b>Embed file</b>",
                           "Select embed file")
            return 0
        else:
            embedFile = ' -ef "' + embedFile + '"'
        # Define the Stego file
        if(self.cover_file_use.get_active()):
            stegoFile = ""
        else:
            if(self.stego_name.get_text() == ""):
                self.show_error("Please enter a <b>Stego filename</b>!",
                               "Enter Stego filename")
                return 0
            else:
                path = self.covfile.get_current_folder()
                stegoFile = ' -sf "' + path + "/" + self.stego_name.get_text() + '"'
        # Set the encryption
        if(self.typecombo.get_active_text() == None):
            algType = ""
        else:
            algType = " " + self.typecombo.get_active_text()
        
        if(self.modecombo.get_active_text() == None):
            if algType == "":
                algMode = " none"
            else:
                algMode = ""
        else:
            algMode = " " + self.modecombo.get_active_text()
        encRypt = " -e" + algType + algMode
        
        # Define the password
        if(self.pass_entry.get_text() == ""):
            self.show_error("Please enter a <b>Passfrase</b> for the extracting",
                           "No Passfrase!")
            return 0
        else:
            passFrase = " -p " + self.pass_entry.get_text()

        # Check the compression
        if(self.do_compress.get_active()):
            comPress = " -Z"
        else:
            comPress = " -z " + self.compress_level.get_text()

        # Create Checksum
        if(self.checksum_check.get_active()):
            checkSum = " -K"
        else:
            checkSum = ""

        # Original name
        if(self.no_orig_name.get_active()):
            origName = " -N"
        else:
            origName = ""

        # Test the output
        self.terminal.feed_child("cd " + self.covfile.get_current_folder() + "\n")
        self.terminal.feed_child("clear \n")
        self.terminal.feed_child("steghide embed" + covFile + embedFile + encRypt + stegoFile + passFrase + comPress + checkSum + origName+"\n")
        self.tabs.set_current_page(2)

    def compress_change(self, button):
        if(self.compress_check.get_active()):
            self.compression_val.set_sensitive(False)
        else:
            self.compression_val.set_sensitive(True)

    def use_cover(self, button):
        if(self.cover_file_use.get_active()):
            self.stego_name.set_sensitive(False)
        else:
            self.stego_name.set_sensitive(True)

    def extract(self, button):
        # Check if a stegfile is specified
        if(self.stegfile.get_text() == ""):
            self.show_error("You must specify a <b>Stego file</b> to extract information from.",
                           'No Stego file specified')
            return 0
        else:
            stegFile = ' -sf "%s"' % self.stegfile.get_text()

        # Check if extract file should be used
        if(self.outputfile.get_sensitive()):
            if(self.outputfile.get_text() != ""):
                outFile = ' -xf "' + self.outputfile.get_text() + '"'
            else:
                self.show_error("Please select a <b>Output file</b> or check the option\n<i>Use original name</i>",
                               'No output filename')
                return 0
        else:
            outFile = " -f"

        # Check for passphrase
        if(self.passfrase.get_text() == ""):
            self.show_error("There is <b>no password</b> specified.\nPlease enter a password",
                           "No Password")
            return 0
        else:
            passPhrase = " -p " + self.passfrase.get_text()

        gopath = os.path.dirname(self.stegfile.get_text())
        self.terminal.feed_child("cd %s\n" % gopath)
        self.terminal.feed_child("clear\n")
        self.terminal.feed_child("steghide extract" + stegFile + outFile + passPhrase + "\n")

    def __init__(self):
        self.window = builder.get_object('window1')
        self.window.set_property('height-request', 300)
        self.window.connect('destroy', self.on_window_destroy)
        self.tabs = builder.get_object('notebook1')
        self.terminal = builder.get_object('terminal1')
        self.terminal.fork_command()
        self.terminal.connect("child-exited",
                              lambda term: self.terminal.fork_command())
        # Execution Tab and its objects 
        self.execbut = builder.get_object('button1')
        self.execbut.connect("clicked", self.embed)
        self.compress_check = builder.get_object('checkbutton2')
        self.compress_check.connect('toggled', self.compress_change)
        self.compression_val = builder.get_object('spinbutton1')
        self.cover_file_use = builder.get_object('checkbutton1')
        self.cover_file_use.set_active(True)
        self.cover_file_use.connect('toggled', self.use_cover)
        self.stego_name = builder.get_object('entry1')
        self.stego_name.set_sensitive(False)
        self.covfile = builder.get_object("filechooserbutton1")
        self.covfile.set_title("Select Cover file:")
        covfilter = gtk.FileFilter()
        covfilter.set_name("Image files")
        covfilter.add_mime_type("image/jpeg")
        covfilter.add_mime_type("image/bmp")
        covfilter.add_pattern("*.jpg")
        covfilter.add_pattern("*.jpeg")
        covfilter.add_pattern("*.bmp")
        self.covfile.add_filter(covfilter)
        covfilter = gtk.FileFilter()
        covfilter.set_name("Audio files")
        covfilter.add_mime_type("audio/basic")
        covfilter.add_mime_type("audio/x-wav")
        covfilter.add_pattern("*.au")
        covfilter.add_pattern("*.mp3")
        covfilter.add_pattern("*.wav")
        self.covfile.add_filter(covfilter)
        self.embedfile = builder.get_object("filechooserbutton2") 
        self.typecombo = builder.get_object("combobox1")
        self.typelist = gtk.ListStore(str)
        text = gtk.CellRendererText()
        self.typecombo.pack_start(text)
        self.typecombo.add_attribute(text, "text", 0)
        self.typecombo.set_model(self.typelist)
        for typ in config["algtypes"]['algoritm']:
            self.typelist.append([typ])
        self.typecombo.connect("changed", self.set_modes)
        self.modecombo = builder.get_object("combobox2")
        self.modelist = gtk.ListStore(str)
        modtxt = gtk.CellRendererText()
        self.modecombo.pack_start(text)
        self.modecombo.add_attribute(text, "text", 0)
        self.modecombo.set_model(self.modelist)
        self.pass_entry = builder.get_object("entry2")
        self.do_compress = builder.get_object("checkbutton2")
        self.compress_level = builder.get_object("spinbutton1")
        self.compress_level.set_value(1.0)
        self.checksum_check = builder.get_object('checkbutton3')
        self.no_orig_name = builder.get_object('checkbutton4')
        
        # Extracting Tab and its objects
        self.extractbut = builder.get_object('button3')
        self.extractbut.connect("clicked", self.extract)
        self.select_stego = builder.get_object('button2')
        self.select_stego.connect("clicked", self.select_file)
        self.stegfile = builder.get_object('entry3')
        self.outputfile = builder.get_object('entry4')
        self.use_original_name = builder.get_object('checkbutton5')
        self.use_original_name.connect('toggled', self.set_use_original)
        self.passfrase = builder.get_object('entry5')

        # Connect the about buttons to actions
        self.website = builder.get_object('button4')
        self.website.connect('clicked', self.open_homepage)
        self.helpuser = builder.get_object('button5')
        self.helpuser.connect('clicked', self.show_help)
        self.quitapp = builder.get_object('button6')
        self.quitapp.connect('clicked', self.confirm_exit)

        self.help_dialog = builder.get_object('helpdialog');
        self.sw = builder.get_object('scrolledwindow1')
        self.help_dialog.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
        self.webview = gtkmozembed.MozEmbed()
        self.webview.load_url("file://"+basepath+"/help/index.html")
        self.sw.add_with_viewport(self.webview)

        self.helpembbtn = builder.get_object('help-embed')
        self.helpembbtn.connect('clicked', self.show_embed_help)
        self.helpextbtn = builder.get_object('help-extract')
        self.helpextbtn.connect('clicked', self.show_extract_help)
        self.helpffmbtn = builder.get_object('help-fileformats')
        self.helpffmbtn.connect('clicked', self.show_formats_help)
        self.helptrmbtn = builder.get_object('help-terminal')
        self.helptrmbtn.connect('clicked', self.show_terminal_help)



    def close_help(self, bitton, data=None):
        self.help_dialog.destroy()

    def select_file(self, button):
        openfile = gtk.FileChooserDialog("Select Stego file:", None,
                                        gtk.FILE_CHOOSER_ACTION_OPEN,
                                        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        filter = gtk.FileFilter()
        filter.set_name("Image files")
        filter.add_mime_type("image/jpeg")
        filter.add_mime_type("image/bmp")
        filter.add_pattern("*.jpg")
        filter.add_pattern("*.jpeg")
        filter.add_pattern("*.bmp")
        openfile.add_filter(filter)
        filter = gtk.FileFilter()
        filter.set_name("Audio files")
        filter.add_mime_type("audio/basic")
        filter.add_mime_type("audio/x-wav")
        filter.add_pattern("*.au")
        filter.add_pattern("*.mp3")
        filter.add_pattern("*.wav")
        openfile.add_filter(filter)

        response = openfile.run()
        if response == gtk.RESPONSE_OK:
            self.stegfile.set_text(openfile.get_filename())
        else:
            pass
        openfile.destroy()

    def open_homepage(self, button):
        try:
            import webbrowser
            webbrowser.open_new("http://code.google.com/p/pysteg")
        except ImportError, e:
            error = gtk.MessageDialog(None,
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE)
            error.set_title("Error")
            error.set_markup("The following error accured:\n%s" % e)
            error.run()
            error.destroy()


    def show_help(self, button):
        self.help_dialog.show_all()
        response = self.help_dialog.run()
        self.webview.load_url("file://"+basepath+"/help/index.html")
        self.help_dialog.hide()

    def show_embed_help(self, button):
        self.webview.load_url("file://"+basepath+"/help/embed.html")

    def show_extract_help(self, button):
        self.webview.load_url("file://"+basepath+"/help/extract.html")

    def show_formats_help(self, button):
        self.webview.load_url("file://"+basepath+"/help/formats.html")

    def show_terminal_help(self, button):
        self.webview.load_url("file://"+basepath+"/help/terminal.html")

    def confirm_exit(self, button):
        quitd = gtk.MessageDialog(None,
                                 gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                 gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO)
        quitd.set_title("Confirm exit")
        quitd.set_markup("Do you really want to <b>quit</b> from pySteg?")
        if(quitd.run() == gtk.RESPONSE_YES):
            gtk.main_quit()
        else:
            quitd.destroy()

    def set_use_original(self, widget, data=None):
        if(self.use_original_name.get_active()):
            self.outputfile.set_sensitive(False)
        else:
            self.outputfile.set_sensitive(True)

    def set_modes(self, widget, data=None):
        self.modelist.clear()
        algtype = widget.get_active_text()
        self.modelist.append([""])
        for mod in config['algmodes'][algtype]:
            if algtype in ['arcfour', 'wake','enigma']:
                self.modelist.append(['stream'])
                break
            self.modelist.append([mod])

    def show_error(self, text, title):
        dialog = gtk.MessageDialog(None,
                                  gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                  gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE)
        dialog.set_title(title)
        dialog.set_markup(text)
        dialog.run()
        dialog.destroy()


if __name__ == "__main__":
    pysteg = PySteg()
    pysteg.window.show()
    gtk.main()
