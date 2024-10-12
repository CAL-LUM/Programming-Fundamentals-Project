import customtkinter
import sqlite3
import bcrypt
from PIL import Image
from tkinter import (messagebox, filedialog)
from datetime import datetime, timedelta
import threading
from io import BytesIO
import qrcode
import os
import re
import cv2


# Create Tkinter application instance window
app = customtkinter.CTk()
app.title('Login') # Set title of application window
app.geometry('1400x900') # Set size of application on launch
app.configure(fg_color='#121212') # Configure background colour of application
app.minsize(1400,900) # Set Minimum size of application

# Font Dictionary
font1 = ('Helvetica', 24, 'bold')
font2 = ('Arial', 18, 'bold') 
font3 = ('Arial', 12, 'bold')
font4 = ('Arial', 12, 'bold', 'underline')
font5 = ('Helvetica', 36, 'bold')
font6 = ('Helvetica', 16)
logofont = ('Arial', 56, 'italic')

# Colour Code Dictionary
bgColourDark = '#121212'
bgColourDark2 = '#212121'
hoverColourDark= '#202020'
hoverColourLight= '#CFCFCF'
borderColourDark= '#66757F'
eventTileDark= '#141414'
buttonColour= '#9A64C5'
whiteColour = '#FFF'
placeHolderColour = '#918c85'

global_image_data = None

# Main page function which displays a majority of functions used within the program, 
# such as scanning QR codes, basket, create event, existing events and favouritesOnly and promotionsOnly parameters to for respective filters on events.
def showMainPage(oldPage=None, oldMainPage=None, search="", promotionsOnly=False, favouritesOnly=False):
    # Destroys previous pages if provided
    if oldPage:
        oldPage.destroy()
    if oldMainPage:
        oldMainPage.destroy()
        
    # Creates a main display frame for the app. Expand=True allows for scrollbar once events overflow frame.
    display = customtkinter.CTkFrame(app, corner_radius=0, fg_color=bgColourDark)
    display.pack(fill="both", expand=True)
    
    # Navigation bar frame setup
    Navbar = customtkinter.CTkFrame(display, corner_radius=0, fg_color=bgColourDark)
    Navbar.pack(fill="both", padx=(0, 30), pady=(0, 2))
    
    # Button colours dynamically change based on page being displayed
    HomeButtonColour = bgColourDark
    PromotionButtonColour = bgColourDark
    FavouritesButtonColour = bgColourDark
    
    #If statement to check which page the user is currently viewing, and change colours accordingly.
    if promotionsOnly:
        PromotionButtonColour = bgColourDark2
    elif favouritesOnly:
        FavouritesButtonColour = bgColourDark2
    else:
        HomeButtonColour = bgColourDark2
    
    # Navigation buttons that use Lambda commands to manage page changes and parameter changes
    HomeButton = customtkinter.CTkButton(Navbar, font=font2, text_color=whiteColour, fg_color=HomeButtonColour, hover_color=bgColourDark2, 
                                         text='Home', width=300,height=50, corner_radius=0, border_width=0, command=lambda: showMainPage(oldMainPage=display))
    HomeButton.grid(column=0, row=0, padx=(5, 0), pady=5, sticky='nesw') 
    
    PromotionButton = customtkinter.CTkButton(Navbar, font=font2, text_color=whiteColour, fg_color=PromotionButtonColour, hover_color=bgColourDark2, 
                                              text='Promotions', width=300, height=50, corner_radius=0, border_width=0, command=lambda: showMainPage(oldMainPage=display, promotionsOnly=True))
    PromotionButton.grid(column=1, row=0, padx=(5, 0), pady=5, sticky='nesw')

    FavouritesButton = customtkinter.CTkButton(Navbar, font=font2, text_color=whiteColour, fg_color=FavouritesButtonColour, hover_color=bgColourDark2, 
                                               text='Favourites', width=300, height=50, corner_radius=0, border_width=0, command=lambda: showMainPage(oldMainPage=display, favouritesOnly=True))
    FavouritesButton.grid(column=2, row=0, padx=(5, 0), pady=5, sticky='nesw')
    
    # Navigation bar frame for buttons
    NavbarActionsFrame = customtkinter.CTkFrame(Navbar, corner_radius=0, fg_color=bgColourDark)
    NavbarActionsFrame.place(relx=1, rely=0.3, anchor='ne')
    
    #Scan QR code button which uses lambda to call ScanQRCode function
    scanQRCode_button = customtkinter.CTkButton(NavbarActionsFrame, text='Scan QR Code', font=font6, text_color=bgColourDark, fg_color=buttonColour, hover_color=hoverColourLight, corner_radius=7, command=lambda: ScanQRCode())
    scanQRCode_button.grid(column=0, row=0, padx=(0,5), sticky='nesw')
    
    #Open Basket button which uses lambda to call showBasket function
    openBasket_button = customtkinter.CTkButton(NavbarActionsFrame, text='Basket', font=font6, text_color=bgColourDark, 
                                                fg_color=buttonColour, hover_color=hoverColourLight, corner_radius=7, command=lambda: ShowBasket())
    openBasket_button.grid(column=1, row=0, padx=(0,5), sticky='nesw')
    
    #Log out button that uses Lambda command to return user to log-in page.
    exitApp_button = customtkinter.CTkButton(NavbarActionsFrame, text='Log out', font=font6, text_color=bgColourDark, fg_color=buttonColour, hover_color=hoverColourLight, corner_radius=7, command=lambda: showLoginPage(oldPage=display,))
    exitApp_button.grid(column=2, row=0, sticky='nesw')
    
    # Main home page frame setup
    HomePage = customtkinter.CTkFrame(display, fg_color=bgColourDark)
    HomePage.pack(fill="both", expand=True)
    
    # Search bar and buttons frame
    ButtonsFrame = customtkinter.CTkFrame(HomePage, height=35, fg_color=bgColourDark)
    ButtonsFrame.pack(fill="both", padx=(30,30))
    ButtonsFrame.grid_columnconfigure(0, weight=1)
    ButtonsFrame.grid_columnconfigure(1, weight=1)
    ButtonsFrame.grid_columnconfigure(2, weight=1)
    ButtonsFrame.grid_columnconfigure(3, weight=1)
    ButtonsFrame.grid_columnconfigure(4, weight=1)
    ButtonsFrame.grid_columnconfigure(5, weight=0)
    ButtonsFrame.grid_columnconfigure(6, weight=1)
    
    # Search entry field which accepts user input
    search_entry = customtkinter.CTkEntry(ButtonsFrame, font=font2, text_color=whiteColour, fg_color=bgColourDark, 
                                          border_color=borderColourDark, border_width=2, placeholder_text='Search...', placeholder_text_color=placeHolderColour, justify="left", corner_radius=8)
    search_entry.grid(row=0, column=0, padx=(0,5), columnspan=5, sticky='nesw')
    if search != "":
        search_entry.insert(0, search)
    
    # Search button which uses Lambda command to display main page and assign user input to 'search' variable.
    searchButton = customtkinter.CTkButton(ButtonsFrame, text='Search', font=font6, text_color=bgColourDark, fg_color=buttonColour, 
                                           hover_color=hoverColourLight, corner_radius=7, command=lambda: showMainPage(oldMainPage=display, search=search_entry.get()))
    searchButton.grid(row=0, column=5, padx=(0, 30), sticky='nesw')

    # Add event button which calls showCreateEventPage, allowing the user to enter a new event into the database.
    addEvent_button = customtkinter.CTkButton(ButtonsFrame, text='Add event', font=font6, text_color=bgColourDark, fg_color=buttonColour, hover_color=hoverColourLight, corner_radius=7, command=lambda: showCreateEventPage(display))
    addEvent_button.grid(row=0, column=6, padx=(30, 0), sticky='nesw')

    # Events display frame
    eventsFrame = customtkinter.CTkFrame(HomePage, fg_color=bgColourDark)
    eventsFrame.pack(fill="both", expand = True)
    eventsFrame.grid_columnconfigure(0, weight=1)
    eventsFrame.grid_columnconfigure(1, weight=1)
    eventsFrame.grid_columnconfigure(2, weight=1)

    # SQL query based on page type and search. 
    # Queries the database based on previous user input retrieved from 'search_entry' and 'searchButton', outputs results based on user input.
    # Further sets limited results dependent on whether user is on main page / promotions / favourites tabs.
    search = search_entry.get()
    # SQL query to search event name, venue, addres and genre for LIKE query. % signs used to allow for partial matches to be displayed.
    searchQuery = "(eventName LIKE ? OR eventVenue LIKE ? OR eventAddress LIKE ? OR eventGenre LIKE ?)"
    searchWildcard = '%' + search + '%'
    
    #If statement to further limit search query results based on current page - promotions/favourites/home.
    if promotionsOnly:
        sqlQuery = 'SELECT * FROM events WHERE eventPromotionDiscount > 0 AND eventPromotionDiscount NOT NULL AND eventPromotionDiscount NOT LIKE "" AND ' + searchQuery
        cursor.execute(sqlQuery, (searchWildcard, searchWildcard, searchWildcard, searchWildcard))
    elif favouritesOnly:
        sqlQuery = 'SELECT * FROM events LEFT JOIN favourites ON events.eventID = favourites.eventID WHERE favourites.userID = ? AND ' + searchQuery
        cursor.execute(sqlQuery, (currentUserID, searchWildcard, searchWildcard, searchWildcard, searchWildcard))
    else:
        sqlQuery = 'SELECT * FROM events WHERE ' + searchQuery
        cursor.execute(sqlQuery, (searchWildcard, searchWildcard, searchWildcard, searchWildcard))
    
    # Fetches existing events based on SQL query above
    existing_events = cursor.fetchall()

    # Row and column counters to track existing event tiles position
    row_count = 0
    col_count = 0
    #Predetermined image size to ensure all images are the same size.
    imageSize = (384,216)
    
    # Loop to sort through existing events
    for event in existing_events:
        #Convert eventID to string to avoid concatenation errors in eventName_label
        event_id = str(event[0])
        # Create events frame to store event tiles within
        event_frame = customtkinter.CTkFrame(eventsFrame, width=347, height=347, corner_radius=15, fg_color=eventTileDark)
        #Management of left and right padding to ensure padding is equal accross row depending on column.
        if col_count == 2:
            event_frame.grid(row=row_count, column=col_count, padx=(30, 30), pady=24, sticky='nesw')
        else:
            event_frame.grid(row=row_count, column=col_count, padx=(30, 0), pady=24, sticky='nesw')

        image_label = customtkinter.CTkLabel(event_frame, text='')
        image_label.place(relx=0.5, rely=0.4, anchor='center')
        
        #Initialise photo_image variable and set value to None.
        photo_image = None

        # Set event image
        if event[10]:
            #Extract image data from event[9]
            image_data = event[10]
            #Open image using BytesIO library
            image = Image.open(BytesIO(image_data))
            # Create CTKimage using opened image and predetermined imageSize.
            photo_image = customtkinter.CTkImage(image, size=imageSize)

        #Configures label to display image.
        image_label.configure(image=photo_image)

        # Binds QR code image to display showEventDetails page on Button-1 click, and QR Code on hover.
        if event[11]:
            #Checks to see if data present in 10th tuple.
            qr_image = Image.open(BytesIO(event[11]))
            #Creates CTKimage using image and predetermined imageSize
            qr_photo_image = customtkinter.CTkImage(qr_image, size=imageSize)
            
            #Display the QRcode upon user mouse cursor entering the event tile
            image_label.bind("<Enter>", lambda e, qr_photo_image=qr_photo_image: e.widget.configure(image=qr_photo_image._get_scaled_light_photo_image(imageSize)))
            #Hide the QRcode upon user mouse cursor exiting the event tile
            image_label.bind("<Leave>", lambda e, photo_image=photo_image: e.widget.configure(image=photo_image._get_scaled_light_photo_image(imageSize)))
            #Binds QRcode to call showEventDetails function using lambda command on Button-1 click.
            image_label.bind("<Button-1>", lambda _, eventId=event_id:showEventDetails(eventId, display))

        # Displays event ID an event Name ontop of frame. 
        eventName_label = customtkinter.CTkLabel(event_frame, text="#" + event_id + ": " + event[2], font=font2, text_color=buttonColour)
        eventName_label.place(relx=0.5, rely=0.8, anchor='center')
        #Binds event tile to call showEventDetails function using lambda command on Button-1 click.
        event_frame.bind("<Button-1>", lambda _, eventId=event_id:showEventDetails(eventId, display))

        #Increment column and row variables to accurately display event tiles in correct position. 'if 'statement utilised to check position of tile
        #if column is column 3, reset column count and increase row.
        col_count += 1
        if col_count == 3:
            col_count = 0
            row_count += 1
        
def showLoginPage(oldPage=None,):
    # Destroy old page if provided
    if oldPage:
        oldPage.destroy()
        
    # Creates frame for the login page
    LogInPage = customtkinter.CTkFrame(app, fg_color=bgColourDark, width=370, height=470, corner_radius=15)
    LogInPage.place(relx=0.5, rely=0.5, anchor='center')
    
    #Creates the TicketWave logo visible on Login and Create Account page.
    login_label = customtkinter.CTkLabel(app, font=logofont, text='TicketWave', text_color=buttonColour)
    login_label.place(relx=0.497, rely=0.15, anchor='center')
    
    #Creates the 'Log in' text on login page.
    login_label1 = customtkinter.CTkLabel(LogInPage, font=font5, text='Log in', text_color=whiteColour)
    login_label1.place(relx=0.497, rely=0.2, anchor='center')

    #Creates entry box for username.
    username_entry = customtkinter.CTkEntry(LogInPage, font=font2, text_color=whiteColour, fg_color=bgColourDark, border_color=borderColourDark, border_width=2, placeholder_text='Username', placeholder_text_color=placeHolderColour, justify="center", width=270, height=50, corner_radius=10)
    username_entry.place(relx=0.5, rely=0.35, anchor='center')

    #Creates entry box for password.
    password_entry = customtkinter.CTkEntry(LogInPage, font=font2, show='*', text_color=whiteColour, fg_color=bgColourDark, border_color=borderColourDark, border_width=2, placeholder_text='Password', placeholder_text_color=placeHolderColour, justify="center", width=270, height=50, corner_radius=10)
    password_entry.place(relx=0.5, rely=0.50, anchor='center')
    
    # Retrieves user input from "username_entry" and "password_entry" and calls logIn function.
    logIn_button = customtkinter.CTkButton(LogInPage, text='Login', font=font6, text_color=bgColourDark, fg_color=buttonColour, hover_color=hoverColourLight, width=270, height=35, command=lambda: LogIn(username_entry.get(), password_entry.get(), LogInPage), corner_radius=7)
    logIn_button.place(relx=0.5, rely=0.7, anchor='center')
    
    # Binds text "Don't have an account? Create one now." to redirect to createAccountPage on Button-1 click.
    CreateAccount_label = customtkinter.CTkLabel(LogInPage, font=font4, text="Don't have an account? Create one now.", text_color=whiteColour)
    CreateAccount_label.bind("<Button-1>", lambda _:showCreateAccountPage(LogInPage))
    CreateAccount_label.place(relx=0.5, rely=0.9, anchor='center')
    

def showCreateAccountPage(oldPage=None):
    # Destroy old page if provided
    if oldPage:
        oldPage.destroy()

    # Creates the create account page frame
    createAccountPage = customtkinter.CTkFrame(app, fg_color=bgColourDark, width=450, height=500, corner_radius=25)
    createAccountPage.place(relx=0.5, rely=0.5, anchor='center')
    #Creates the 'Create Account' text on login page.
    CreateAccount_label = customtkinter.CTkLabel(createAccountPage, font=font5, text='Create Account', text_color=whiteColour)
    CreateAccount_label.place(relx=0.497, rely=0.1, anchor='center')
    #Creates entry box for username.
    username_entry = customtkinter.CTkEntry(createAccountPage, font=font2, text_color=whiteColour, fg_color=bgColourDark, border_color=borderColourDark, border_width=2, placeholder_text='Username', placeholder_text_color=placeHolderColour, justify="center",width=270, height=50, corner_radius=10)
    username_entry.place(relx=0.5, rely=0.25, anchor='center')
    #Creates entry box for password.
    password_entry = customtkinter.CTkEntry(createAccountPage, font=font2, show='*', text_color=whiteColour, fg_color=bgColourDark, border_color=borderColourDark, border_width=2, placeholder_text='Password', placeholder_text_color=placeHolderColour, justify="center", width=270, height=50, corner_radius=10)
    password_entry.place(relx=0.5, rely=0.38, anchor='center')
    #Creates entrry box for email.
    email_entry = customtkinter.CTkEntry(createAccountPage, font=font2, text_color=whiteColour, fg_color=bgColourDark, border_color=borderColourDark, border_width=2, placeholder_text='Email address', placeholder_text_color=placeHolderColour, justify="center", width=270, height=50, corner_radius=10)
    email_entry.place(relx=0.5, rely=0.51, anchor='center')
    #Creates entry box for date of birth.
    dob_entry = customtkinter.CTkEntry(createAccountPage, font=font2, text_color=whiteColour, fg_color=bgColourDark, border_color=borderColourDark, border_width=2, placeholder_text='Date of birth (DD/MM/YYYY)', placeholder_text_color=placeHolderColour, justify="center", width=270, height=50, corner_radius=10)
    dob_entry.place(relx=0.5, rely=0.64, anchor='center')

    # Retrieves user input from 'username_entry, password_entry, email_entry, and dob_entry' and calls create_account function.
    create_account_button = customtkinter.CTkButton(createAccountPage, text='Create Account', font=font6, text_color=bgColourDark, fg_color=buttonColour, hover_color=hoverColourLight, width=250, height=35, command=lambda: create_account(username_entry.get(), password_entry.get(), email_entry.get(), dob_entry.get(), createAccountPage), corner_radius=7)
    create_account_button.place(relx=0.5, rely=0.8, anchor='center')

    # Binds text "Already have an account? Log in." to redirect to LogInPage on Button-1 click using lambda command.
    login_label = customtkinter.CTkLabel(createAccountPage, font=font4, text="Already have an account? Log in.", text_color=whiteColour)
    login_label.bind("<Button-1>", lambda _:showLoginPage(createAccountPage))
    login_label.place(relx=0.5, rely=0.9, anchor='center')

def showCreateEventPage(oldMainPage):
 
    # Creates the create event page frame
    CreateEventPage = customtkinter.CTkFrame(app, fg_color=bgColourDark, width=850, height=520, border_color=borderColourDark, border_width=2, corner_radius=15 )
    CreateEventPage.place(relx=0.5, rely=0.5, anchor='center')
    #Creates label for 'Add an event to ticket wave!'
    CreateEvent_label = customtkinter.CTkLabel(CreateEventPage, font=font1, text='Add an event to Ticket Wave!', text_color=whiteColour)
    CreateEvent_label.place(relx=0.5, rely=0.1, anchor='center')
    
    # Various event entry fields to collect event data.
    eventName_entry = customtkinter.CTkEntry(CreateEventPage, font=font2, text_color=whiteColour, fg_color=bgColourDark, border_color=borderColourDark, border_width=2, placeholder_text='Name', placeholder_text_color=placeHolderColour, justify="left",width=400, height=40, corner_radius=10)
    eventName_entry.place(relx=0.5, rely=0.20, anchor='ne')
    
    #Creates entry box for venue
    eventVenue_entry = customtkinter.CTkEntry(CreateEventPage, font=font2, text_color=whiteColour, fg_color=bgColourDark, border_color=borderColourDark, border_width=2, placeholder_text='Venue', placeholder_text_color=placeHolderColour, justify="left",width=400, height=40, corner_radius=10)
    eventVenue_entry.place(relx=0.5, rely=0.30, anchor='ne')
    
    #Creates entry box for event ticket price
    eventTicketPrice_entry = customtkinter.CTkEntry(CreateEventPage, font=font2, text_color=whiteColour, fg_color=bgColourDark, border_color=borderColourDark, border_width=2, placeholder_text='Ticket price', placeholder_text_color=placeHolderColour, justify="left",width=195, height=40, corner_radius=10)
    eventTicketPrice_entry.place(relx=0.259, rely=0.40, anchor='ne')
    
    #Creates entry box for event ticket quantity
    eventTicketQuantity_entry = customtkinter.CTkEntry(CreateEventPage, font=font2, text_color=whiteColour, fg_color=bgColourDark, border_color=borderColourDark, border_width=2, placeholder_text='Ticket quantity', placeholder_text_color=placeHolderColour, justify="left",width=195, height=40, corner_radius=10)
    eventTicketQuantity_entry.place(relx=0.500, rely=0.40, anchor='ne')
    
    #Creates entry box for event genre
    eventGenre_entry = customtkinter.CTkEntry(CreateEventPage, font=font2, text_color=whiteColour, fg_color=bgColourDark, border_color=borderColourDark, border_width=2, placeholder_text='Genre', placeholder_text_color=placeHolderColour, justify="left",width=195, height=40, corner_radius=10)
    eventGenre_entry.place(relx=0.259, rely=0.50, anchor='ne')
    
    #Creates entry box for event month
    eventMonth_entry = customtkinter.CTkEntry(CreateEventPage, font=font2, text_color=whiteColour, fg_color=bgColourDark, border_color=borderColourDark, border_width=2, placeholder_text='Month', placeholder_text_color=placeHolderColour, justify="left",width=92, height=40, corner_radius=10)
    eventMonth_entry.place(relx=0.379, rely=0.50, anchor='ne')
    
    #Creates entry box for event day
    eventDay_entry = customtkinter.CTkEntry(CreateEventPage, font=font2, text_color=whiteColour, fg_color=bgColourDark, border_color=borderColourDark, border_width=2, placeholder_text='Day', placeholder_text_color=placeHolderColour, justify="left",width=92, height=40, corner_radius=10)
    eventDay_entry.place(relx=0.5, rely=0.50, anchor='ne')
    
    #Creates entry box for event address
    eventAddress_entry = customtkinter.CTkEntry(CreateEventPage, font=font2, text_color=whiteColour, fg_color=bgColourDark, border_color=borderColourDark, border_width=2, placeholder_text='Address', placeholder_text_color=placeHolderColour, justify="left",width=400, height=40, corner_radius=10)
    eventAddress_entry.place(relx=0.5, rely=0.60, anchor='ne')
    
    #Creates entry box for event promotion
    eventPromotionDiscount_entry = customtkinter.CTkEntry(CreateEventPage, font=font2, text_color=whiteColour, fg_color=bgColourDark, border_color=borderColourDark, border_width=2, placeholder_text='Promotion discount (optional)', placeholder_text_color=placeHolderColour, justify="left",width=400, height=40, corner_radius=10)
    eventPromotionDiscount_entry.place(relx=0.5, rely=0.70, anchor='ne')
    
    #Creates entry box for event description
    eventDescription_entry = customtkinter.CTkTextbox(CreateEventPage, font=font2, text_color=whiteColour, fg_color=bgColourDark, border_color=borderColourDark, border_width=2,width=390, height=248, corner_radius=10)
    eventDescription_entry.place(relx=0.515, rely=0.2, anchor='nw')
    
    # Retrieves user input from entry fields and calls addEvent function.
    CreateEvent_Button = customtkinter.CTkButton(CreateEventPage, text='Add event', font=font6, text_color=bgColourDark, fg_color=buttonColour, hover_color=hoverColourLight, width=300, height=40, command=lambda: addEvent(eventName_entry.get(), eventDay_entry.get(), eventMonth_entry.get(), eventVenue_entry.get(), eventAddress_entry.get(), eventGenre_entry.get(), eventTicketPrice_entry.get(), eventDescription_entry.get("1.0", "end-1c"), eventTicketQuantity_entry.get(), eventPromotionDiscount_entry.get(), global_image_data, CreateEventPage, oldMainPage), corner_radius=7)
    CreateEvent_Button.place(relx=0.33, rely=0.85, anchor='nw')
    
    # Simple button to close createEventPage and return to ShowMainPage.
    CloseEventCreate_Button = customtkinter.CTkButton(CreateEventPage, text='X', font=font6, text_color=whiteColour, fg_color=bgColourDark, width=16, height=15, hover_color=buttonColour, command=lambda: showMainPage(CreateEventPage, oldMainPage))
    CloseEventCreate_Button.place(relx=0.96, rely=0.02)
    
    # Function to upload image to event
    def upload_image():
        #Declare global_image_data as global variable
        global global_image_data
        # Opens a file dialog to select an image file, limited to .png, .jpg, .jpeg and .gif
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
        # Checks if a file was selected
        if file_path:
            # Opens selected file in binary and sets global_image_data to contain this binary data.
            with open(file_path, 'rb') as file:
                global_image_data = file.read()

    # Upload image button which calls the upload_image function above. 
    uploadImage_Button = customtkinter.CTkButton(CreateEventPage, text='Upload Image', font=font2, text_color=whiteColour, fg_color=bgColourDark, border_color=borderColourDark, hover_color=hoverColourDark, border_width=2, width=390, height=40, command=upload_image, corner_radius=10)
    uploadImage_Button.place(relx=0.515, rely=0.70, anchor='nw')    
    
    #Resets global_image_data variable
    global global_image_data
    global_image_data = None
    
    # Function to validate user inputs upon event creation.
def validate_inputs(eventName, eventDay, eventMonth, eventVenue, eventAddress, eventGenre, eventTicketPrice, eventDescription, eventTicketQuantity, eventPromotionDiscount, eventImageData):
    
    # Validate eventName entry
    if not (eventName and len(eventName) >= 3 and all(char.isalpha() or char.isspace() for char in eventName)):
        return False, "Event name is required and must be at least 3 characters long, (no numbers or special characters)."

    # Validate eventVenue entry
    if not (eventVenue and len(eventVenue) >= 3 and all(char.isalnum() or char.isspace() for char in eventVenue)):
        return False, "Event venue is required and must be at least 3 characters long, (no special characters)."

    # Validate eventTicketPrice entry
    try:
        eventTicketPrice = int(eventTicketPrice)
    except ValueError:
        return False, "Event ticket price is required and must be a number."

    # Validate eventTicketQuantity entry
    try:
        eventTicketQuantity = int(eventTicketQuantity)
    except ValueError:
        return False, "Event ticket quantity is required and must be a number."

    # Validate eventGenre entry
    if not (eventGenre and len(eventGenre) >= 3 and all(char.isalpha() or char.isspace() for char in eventGenre)):
        return False, "Event genre is required and must be at least 3 characters long, (no numbers or special characters)."

    # Validate eventMonth entry
    try:
        eventMonth = int(eventMonth)
        if not (1 <= eventMonth <= 12):
            raise ValueError()
    except ValueError:
        return False, "Event month is required and must be a number between 1 and 12."

    # Validate eventDay entry
    try:
        eventDay = int(eventDay)
        if not (1 <= eventDay <= 31):
            raise ValueError()
    except ValueError:
        return False, "Event day is required and must be a number between 1 and 31."

    # Validate eventAddress entry
    if not (eventAddress and len(eventAddress) >= 3 and all(char.isalnum() or char.isspace() or char in (',', '.') for char in eventAddress)):
        return False, "Event address is required and must be at least 3 characters long, (no special characters)."

    # Validate eventPromotionDiscount entry
    if eventPromotionDiscount:
        try:
            eventPromotionDiscount = int(eventPromotionDiscount)
        except ValueError:
            return False, "Event promotion discount must be a number."

    # Validate eventDescription entry
    if not eventDescription:
        return False, "Event description is required."

    if eventImageData == None:
        return False, "Event image not uploaded."

    return True, None

# Function add events to database
def addEvent(eventName, eventDay, eventMonth, eventVenue, eventAddress, eventGenre, eventTicketPrice, eventDescription, eventTicketQuantity, eventPromotionDiscount, eventImageData, oldPage=None, oldMainPage=None):

    global currentUserID
    #Validate all user inputs
    is_valid, error_message = validate_inputs(eventName, eventDay, eventMonth, eventVenue, eventAddress, eventGenre, eventTicketPrice, eventDescription, eventTicketQuantity, eventPromotionDiscount, eventImageData)

    # Error message to catch any errors.
    if not is_valid:
        messagebox.showerror("Error", error_message)
        return

    # Destroys old pages if provided
    if oldPage:
        oldPage.destroy()

    if oldMainPage:
        oldMainPage.destroy()

    # Inserts event details into the database, input retrieved from user input in create event function
    cursor.execute('INSERT INTO events (eventName, userID, eventDay, eventMonth, eventVenue, eventAddress, eventGenre, eventTicketPrice, eventDescription, eventImage, eventTicketQuantity, eventPromotionDiscount) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                   (eventName, currentUserID, eventDay, eventMonth, eventVenue, eventAddress, eventGenre, eventTicketPrice, eventDescription, eventImageData, eventTicketQuantity, eventPromotionDiscount))
    conn.commit()

    # Retrieves the last inserted row ID
    cursor.execute('SELECT last_insert_rowid()')
    eventID = cursor.fetchone()[0]

    # Creates a directory folder for the QR codes
    if not os.path.exists(os.path.join(os.getcwd(), 'qrcodes')):
        os.makedirs(os.path.join(os.getcwd(), 'qrcodes'))
        
     # Sets parameters for QR Code
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    # Adds data and creates the QR code
    qr.add_data(str(eventID))
    qr.make(fit=True)
    # Sets colour parameters for QR Code
    qr_image = qr.make_image(fill_color="black", back_color="white")
    # Converts to binary
    qr_image_buffer = BytesIO()
    # Saves file in 'qrcodes' directory
    qr_image.save(os.path.join(os.getcwd(), 'qrcodes', 'event'+str(eventID)+'.png'))
    # Formats qrcode to .png
    qr_image.save(qr_image_buffer, format="PNG") 
    qr_image_data = qr_image_buffer.getvalue()

    # Updates the event with the QR code in the database
    cursor.execute('UPDATE events SET qrCode = ? WHERE eventID = ?', (qr_image_data, eventID))
    conn.commit()

    # Redirects the user to the main page.
    showMainPage(oldMainPage)
    
def showEventDetails(eventID, oldMainPage):
    # Fetches event details from database
    cursor.execute('SELECT * FROM events WHERE eventID = ?', (eventID))
    event = cursor.fetchone()
    # Sets tuple associated with eventPromotionDiscount
    eventPromotionDiscount = event[13]
    userID = event[1]

    # Creates the event details popup window
    EventDetailsPopup = customtkinter.CTkFrame(app, fg_color=bgColourDark, bg_color="transparent", border_color=borderColourDark, border_width=2, corner_radius=15)
    EventDetailsPopup.place(relx=0.5, rely=0.5, anchor='center')
    
    # Creates the frame for event details popup
    EventDetailsPage = customtkinter.CTkFrame(EventDetailsPopup, fg_color=bgColourDark, border_width=0)
    EventDetailsPage.pack(fill="both", pady=5, padx=15)
    
    #Configures the frame grid
    EventDetailsPage.grid_columnconfigure(0, weight=1)
    EventDetailsPage.grid_columnconfigure(1, weight=1)
    EventDetailsPage.grid_columnconfigure(2, weight=1)
    
    #Creates label to display 'Event Details' on 'EventDetailsPage'
    eventDetailslabel = customtkinter.CTkLabel(EventDetailsPage, font=font1, text='Event details', text_color=whiteColour, height=80)
    eventDetailslabel.grid(row=0, column=0, columnspan=4, sticky="new", pady=(0, 10))
    
    #Creates frame to store the event name and event name label within it.
    eventNameFrame = customtkinter.CTkFrame(EventDetailsPage, fg_color=borderColourDark, corner_radius=6, border_width=0)
    eventNameFrame.grid(row=1, column=1, sticky="new", pady=(0,12))
    eventName = customtkinter.CTkLabel(eventNameFrame, font=font6, text_color=whiteColour, width=200, fg_color=bgColourDark, text=event[2], justify="left", corner_radius=6, anchor='nw')
    eventName.pack(fill="both", pady=2, padx=2)
    
    eventNameLabel = customtkinter.CTkLabel(EventDetailsPage, font=font2, text_color=whiteColour, text='Event Name', anchor="ne")
    eventNameLabel.grid(row=1, column=0, sticky="new", padx=(0,5))
    
    #Creates frame to store the event venue name and event venue name label within it.
    eventVenueFrame = customtkinter.CTkFrame(EventDetailsPage, fg_color=borderColourDark, corner_radius=6, border_width=0)
    eventVenueFrame.grid(row=2, column=1, sticky="new", pady=(0,5))
    eventVenue = customtkinter.CTkLabel(eventVenueFrame, font=font6, text_color=whiteColour, fg_color=bgColourDark, text=event[5], justify="left", corner_radius=6, anchor='nw')
    eventVenue.pack(fill="both", pady=2, padx=2)
    
    eventVenueLabel = customtkinter.CTkLabel(EventDetailsPage, font=font2, text_color=whiteColour, text='Venue', anchor="ne")
    eventVenueLabel.grid(row=2, column=0, sticky="new", padx=(0,5))
    
    #Creates frame to store the event genre and event genre label within it.
    eventGenreFrame = customtkinter.CTkFrame(EventDetailsPage, fg_color=borderColourDark, corner_radius=6, border_width=0)
    eventGenreFrame.grid(row=3, column=1, sticky="new", pady=(0,5))
    eventGenre = customtkinter.CTkLabel(eventGenreFrame, font=font6, text_color=whiteColour, fg_color=bgColourDark, text=event[7], justify="left", corner_radius=6, anchor='nw')
    eventGenre.pack(fill="both", pady=2, padx=2)
    
    eventGenreLabel = customtkinter.CTkLabel(EventDetailsPage, font=font2, text_color=whiteColour, text='Genre', anchor="ne")
    eventGenreLabel.grid(row=3, column=0, sticky="new", padx=(0,5))
    
    #Creates frame to store the event address and event address label within it.
    eventAddressFrame = customtkinter.CTkFrame(EventDetailsPage, fg_color=borderColourDark, corner_radius=6, border_width=0)
    eventAddressFrame.grid(row=4, column=1, sticky="new", pady=(0,5))
    eventAddress = customtkinter.CTkLabel(eventAddressFrame, font=font6, text_color=whiteColour, fg_color=bgColourDark, text=event[6], justify="left", corner_radius=6, anchor='nw')
    eventAddress.pack(fill="both", pady=2, padx=2)
    
    eventAddressLabel = customtkinter.CTkLabel(EventDetailsPage, font=font2, text_color=whiteColour, text='Address', anchor="ne")
    eventAddressLabel.grid(row=4, column=0, sticky="new", padx=(0,5))
    
    #Creates frame to store the event datea and event date label within it.
    eventDateFrame = customtkinter.CTkFrame(EventDetailsPage, fg_color=borderColourDark, corner_radius=6, border_width=0)
    eventDateFrame.grid(row=5, column=1, sticky="new", pady=(0,5))
    eventDate = customtkinter.CTkLabel(eventDateFrame, font=font6, text_color=whiteColour, fg_color=bgColourDark, text=str(event[3])+"/"+str(event[4])+" (DD/MM)", justify="left", corner_radius=6, anchor='nw')
    eventDate.pack(fill="both", pady=2, padx=2)
    
    eventDateLabel = customtkinter.CTkLabel(EventDetailsPage, font=font2, text_color=whiteColour, text='Date', anchor="ne")
    eventDateLabel.grid(row=5, column=0, sticky="new", padx=(0,5))
    
    #If statement to display 'delete event' button if currentUserID matches userID present in events table
    if currentUserID == userID:
        
        deleteEventButton = customtkinter.CTkButton(EventDetailsPage, text='Delete Event', font=font6, text_color='#922323', fg_color=bgColourDark, width=40, height=15, hover_color=buttonColour, command=lambda: deleteEvent(event[0], EventDetailsPage, EventDetailsPopup, oldMainPage))
        deleteEventButton.grid(row=0, column=2, sticky="ne")
    
    # Checks if event has promotional discount. If present, displays new price of ticket with % of discount. If not present, display original price.
    if eventPromotionDiscount == '':
    
        eventTicketPriceFrame = customtkinter.CTkFrame(EventDetailsPage, fg_color=borderColourDark, corner_radius=6, border_width=0)
        eventTicketPriceFrame.grid(row=6, column=1, sticky="new", pady=(0,5))
        eventTicketPrice = customtkinter.CTkLabel(eventTicketPriceFrame, font=font6, text_color=whiteColour, fg_color=bgColourDark, 
                                                  text=event[8], justify="left", corner_radius=6, anchor='nw')
        eventTicketPrice.pack(fill="both", pady=2, padx=2)
        
    else:
        eventTicketPricePromotion = str(event[8] - ((eventPromotionDiscount / 100) * event[8])) # Displays new ticket price and % discount.
        eventTicketPriceFrame = customtkinter.CTkFrame(EventDetailsPage, fg_color=borderColourDark, corner_radius=6, border_width=0)
        eventTicketPriceFrame.grid(row=6, column=1, sticky="new", pady=(0,5))
        eventTicketPrice = customtkinter.CTkLabel(eventTicketPriceFrame, font=font6, text_color=whiteColour, fg_color=bgColourDark, 
                                                  text=eventTicketPricePromotion + " " +str(event[13]) + "% off", justify="left", corner_radius=6, anchor='nw')
        eventTicketPrice.pack(fill="both", pady=2, padx=2)
    
    eventTicketPriceLabel = customtkinter.CTkLabel(EventDetailsPage, font=font2, text_color=whiteColour, text='Ticket price', anchor="ne")
    eventTicketPriceLabel.grid(row=6, column=0, sticky="new", padx=(0,5))
    
    #Creates frame to store the event ticket quantity and event ticket quantity within it.
    eventTicketQuantityFrame = customtkinter.CTkFrame(EventDetailsPage, fg_color=borderColourDark, corner_radius=6, border_width=0)
    eventTicketQuantityFrame.grid(row=7, column=1, sticky="new", pady=(0,5))
    eventTicketQuantity = customtkinter.CTkLabel(eventTicketQuantityFrame, font=font6, text_color=whiteColour, fg_color=bgColourDark, text=event[12], justify="left", corner_radius=6, anchor='nw')
    eventTicketQuantity.pack(fill="both", pady=2, padx=2)
    
    eventTicketQuantityLabel = customtkinter.CTkLabel(EventDetailsPage, font=font2, text_color=whiteColour, text='Tickets Available', anchor="ne")
    eventTicketQuantityLabel.grid(row=7, column=0, sticky="new", padx=(0,5))
    
    #Creates frame to store the event description and event description within it.
    eventDescriptionFrame = customtkinter.CTkFrame(EventDetailsPage, fg_color=borderColourDark, corner_radius=6, border_width=0)
    eventDescriptionFrame.grid(row=2, column=2, rowspan=6, sticky="new", pady=(0, 13), padx=(15, 0))
    eventDescription = customtkinter.CTkLabel(eventDescriptionFrame, font=font6, text_color=whiteColour, fg_color=bgColourDark, text=event[9], anchor='nw',width=330, height=250, corner_radius=6)
    eventDescription.pack(fill="both", pady=2, padx=2)

    eventDescriptionLabel = customtkinter.CTkLabel(EventDetailsPage, font=font2, text_color=whiteColour, text='Event Description')
    eventDescriptionLabel.grid(row=1, column=2, sticky="new")
    
    #Creates button to destroy the eventdetails popujp
    CloseEventDetails_Button = customtkinter.CTkButton(EventDetailsPage, text='X', font=font6, text_color=whiteColour, fg_color=bgColourDark, width=16, height=15, hover_color=buttonColour, command=lambda: EventDetailsPopup.destroy())
    CloseEventDetails_Button.grid(row=0, column=3, sticky="ne")
    
    #Creates buy tickets button that uses lambda command to call AddToBasket function
    BuyTickets_Button = customtkinter.CTkButton(EventDetailsPage, text='Add ticket to basket', font=font6, text_color=bgColourDark, fg_color=buttonColour, hover_color=hoverColourLight, command=lambda: AddToBasket(event[0], EventDetailsPopup))
    BuyTickets_Button.grid(row=8, column=0, columnspan=4, sticky="nesw", padx=40, pady=(8, 10))

    # Selects from favourites where userID and eventID match
    cursor.execute('SELECT * FROM favourites WHERE userID = ? AND eventID = ?', (str(currentUserID), str(eventID)))
    
    #Fetch existing entries
    existing_entry = cursor.fetchone()

    #'if' statement used to dynamically change favourites button to add or remove based on whether event is present in favourites table.
    if existing_entry:
        RemoveFavourites_Button = customtkinter.CTkButton(EventDetailsPage, text='Remove event from favourites', font=font6, text_color=bgColourDark, fg_color=buttonColour, hover_color=hoverColourLight, command=lambda: RemoveFromFavourites(event[0], EventDetailsPopup))
        RemoveFavourites_Button.grid(row=9, column=0, columnspan=4, sticky="nesw", padx=40, pady=(8, 10))  

    else:
        Favourites_Button = customtkinter.CTkButton(EventDetailsPage, text='Add event to favourites', font=font6, text_color=bgColourDark, fg_color=buttonColour, hover_color=hoverColourLight, command=lambda: AddToFavourites(event[0], EventDetailsPopup))
        Favourites_Button.grid(row=9, column=0, columnspan=4, sticky="nesw", padx=40, pady=(8, 10))

# Function to delete events
def deleteEvent(eventID, oldMainPage, EventDetailsPage, EventDetailsPopup):
    
    # Destroys oldMainPage as 'ShowMainPage()' refreshes
    if oldMainPage:
        oldMainPage.destroy()
    if EventDetailsPage:
        EventDetailsPage.destroy()
    if EventDetailsPopup:
        EventDetailsPopup.destroy()
    
    # Delete event from baskets table
    cursor.execute('DELETE FROM baskets WHERE eventID = ?', (eventID,))
    # Delete event from favourites table
    cursor.execute('DELETE FROM favourites WHERE eventID = ?', (eventID,))
    # Delete event from events table
    cursor.execute('DELETE FROM events WHERE eventID = ?', (eventID,))
    
    # Check if there is a QR code present in the 'qrcodes' folder with the associated eventID
    qr_code_file_path = os.path.join(os.getcwd(), 'qrcodes', 'event'+str(eventID)+'.png')
    
    # Delete QR Code iamage
    if os.path.exists(qr_code_file_path):
        os.remove(qr_code_file_path)
    
    # Commit changes to database
    conn.commit()
    # Refresh main page.
    showMainPage()

def RemoveFromFavourites(eventID, EventDetailsPage):
    # Checks if event details page exists and destroys it.
    if EventDetailsPage:
        EventDetailsPage.destroy()

        # Deletes record from favourites table
        cursor.execute('DELETE FROM favourites WHERE userID = ? AND eventID = ?', (currentUserID, eventID))
        conn.commit()
        
        # Displays a success message.
        messagebox.showinfo('Success', 'Event has been removed from your favourites.')
        
def AddToFavourites(eventID, EventDetailsPage):
    # Checks if event details page exists and destroys it.
    if EventDetailsPage:
        EventDetailsPage.destroy()
        
        # Inserts record into favourites table.
        cursor.execute('INSERT INTO favourites (userID, eventID) VALUES (?, ?)', (currentUserID, eventID))
        conn.commit()

        # Display a success message.
        messagebox.showinfo('Success', 'Event has been added to your favourites.')

# Function to show users basket
def ShowBasket():
    # Retrieves the user's basket items from the database.
    cursor.execute('SELECT * FROM baskets WHERE userID = ?', (str(currentUserID)))
    basket = cursor.fetchall()
    
    # Creates the basket display page
    ShowBasketPage = customtkinter.CTkFrame(app, fg_color=bgColourDark, width=550, height=400, border_color=borderColourDark, border_width=2, corner_radius=15)
    ShowBasketPage.place(relx=0.985, rely=0.059, anchor='ne')
    
    # Create label to display event name title
    eventNameTitle = customtkinter.CTkLabel(ShowBasketPage, font=font2, text_color=whiteColour, fg_color=bgColourDark, text='Event Name', anchor='nw', width=100, height=40, corner_radius=6)
    eventNameTitle.place(relx=0.05, rely=0.05)
    
    # Create label to display event date title
    eventDateTitle = customtkinter.CTkLabel(ShowBasketPage, font=font2, text_color=whiteColour, fg_color=bgColourDark, text='Date', anchor='nw', width=100, height=40, corner_radius=6)
    eventDateTitle.place(relx=0.45, rely=0.05)
    
    # Create label to display event tickets quantity title
    eventTicketsTitle = customtkinter.CTkLabel(ShowBasketPage, font=font2, text_color=whiteColour, fg_color=bgColourDark, text='Tickets', anchor='nw', width=100, height=40, corner_radius=6)
    eventTicketsTitle.place(relx=0.58, rely=0.05)
    
    # Create label to display event tickets price title
    eventPriceTitle = customtkinter.CTkLabel(ShowBasketPage, font=font2, text_color=whiteColour, fg_color=bgColourDark, text='Total Price', anchor='nw', width=100, height=40, corner_radius=6)
    eventPriceTitle.place(relx=0.78, rely=0.05)
    
    # Set itemNum to 0 at the start.
    itemNum = 0
    
    # 'for' loop used to display each item in the basket. 
    for basketItem in basket:
        eventID = basketItem[1]
        
        # Retrieves the event details from the events table.
        cursor.execute('SELECT eventName, eventDay, eventMonth, eventTicketPrice, eventPromotionDiscount FROM events WHERE eventID = ?', (str(eventID)))
        event_details = cursor.fetchone()

        # Retrieves the user-specific ticket quantity and calculates ticket price.
        eventUserTicketQuantity = basketItem[2]
        eventUserTicketPrice = event_details[3]
        
        # Applies promotion if applicable. 
        if event_details[4] and event_details[4] != "":
            eventUserTicketPrice = eventUserTicketPrice - (eventUserTicketPrice * (event_details[4]/100))
        
        # Calculate total price
        totalPrice = eventUserTicketQuantity * eventUserTicketPrice
        
        # Create label to display event name
        eventName = customtkinter.CTkLabel(ShowBasketPage, font=font6, text_color=whiteColour, fg_color=bgColourDark, text=event_details[0], anchor='nw', width=120, height=60, corner_radius=6)
        eventName.place(relx=0.05, rely=0.15 + (0.08 * itemNum))
        
        # Create label to display event date
        eventDateDay = customtkinter.CTkLabel(ShowBasketPage, font=font6, text_color=whiteColour, fg_color=bgColourDark, text=str(event_details[1])+"/"+str(event_details[2]), anchor='nw', width=60, height=40, corner_radius=6)
        eventDateDay.place(relx=0.45, rely=0.15 + (0.08 * itemNum))
        
        # Create label to display event tickets quanntity
        eventTickets = customtkinter.CTkLabel(ShowBasketPage, font=font6, text_color=whiteColour, fg_color=bgColourDark, text=eventUserTicketQuantity, anchor='nw', width=120, height=60, corner_radius=6)
        eventTickets.place(relx=0.58, rely=0.15 + (0.08 * itemNum))
        
        # Create label to display event tickets price
        eventTotalPrice = customtkinter.CTkLabel(ShowBasketPage, font=font6, text_color=whiteColour, fg_color=bgColourDark, text="£"+str(totalPrice), anchor='nw', width=120, height=60, corner_radius=6)
        eventTotalPrice.place(relx=0.78, rely=0.15 + (0.08 * itemNum))
        
        # Creates button that uses lambda to call removeTicketsFromBasket function. 
        removeTicket = customtkinter.CTkButton(ShowBasketPage, text='X', font=font6, text_color='#922323', fg_color=bgColourDark, width=16, height=15, hover_color=buttonColour, command=lambda userID=currentUserID, eventID=eventID: removeTicketFromBasket(userID, eventID, ShowBasketPage))
        removeTicket.bind("<Button-1>", lambda _: removeTicketFromBasket(currentUserID, eventID))
        removeTicket.place(relx=0.90, rely=0.143 + (0.08 * itemNum))
        
        # Set itemNum to +1 at the end so that each ticket is displayed on an individual line one after the other. 
        itemNum += 1
    
    # Close button to destroy the basket display page.
    CloseBasketPage_Button = customtkinter.CTkButton(ShowBasketPage, text='X', font=font6, text_color=whiteColour, fg_color=bgColourDark, width=16, height=15, hover_color=buttonColour, command=lambda: ShowBasketPage.destroy())
    CloseBasketPage_Button.place(relx=0.94, rely=0.02)
    

def AddToBasket(eventID, EventDetailsPage):
    # Destroys the event details page if it exists.
    if EventDetailsPage:
        EventDetailsPage.destroy()

    # Retrieves the event details from the events database table.
    cursor.execute('SELECT * FROM events WHERE eventID = ?', (str(eventID),))
    event = cursor.fetchone()
    eventTicketQuantity = event[12] # Extracts ticket quantity from events table
    eventTicketPrice = event[8] # Extracts ticket price from event table

    #If statement to check if there are available tickets left for the event.
    if eventTicketQuantity > 0:
        cursor.execute('SELECT * FROM baskets WHERE eventID = ? AND userID = ?', (eventID, currentUserID))
        existing_ticket = cursor.fetchone()

        #If statement to check if the user has an existing ticket, if True, eventUserTicketQuantity set to increase by +1
        if existing_ticket:
            eventUserTicketQuantity = existing_ticket[2] + 1
            updatedTotalPrice = eventUserTicketQuantity * eventTicketPrice
            cursor.execute('UPDATE baskets SET quantity = ?, totalPrice = ? WHERE eventID = ? AND userID = ?', (eventUserTicketQuantity, updatedTotalPrice, eventID, currentUserID))
            conn.commit()
        #Else condition to set eventUserTicketQuantity to 1 if no prior existing ticket.
        else:
            eventUserTicketQuantity = 1
            cursor.execute('INSERT INTO baskets (eventID, userID, quantity, totalPrice) VALUES (?, ?, ?, ?)', (eventID, currentUserID, eventUserTicketQuantity, eventTicketPrice))
            conn.commit()

        # Update the event ticket quantity in the events table.
        cursor.execute('UPDATE events SET eventTicketQuantity = ? WHERE eventID = ?', (eventTicketQuantity - 1, eventID))
        conn.commit()

        #Display success message if tickets are sucsessfully added  
        messagebox.showinfo('Success', 'Ticket has been added to your basket.')
        
    #Display error message if event is sold out, occurs when eventTicketQuantity is 0.    
    else:
        messagebox.showinfo('Error', 'Sorry, this event is sold out.')
        
def removeTicketFromBasket(userID, eventID, ShowBasketPage):
    if ShowBasketPage:
        ShowBasketPage.destroy()

    # Check if the ticket is in the user's basket
    cursor.execute('SELECT * FROM baskets WHERE eventID = ? AND userID = ?', (eventID, userID))
    existing_ticket = cursor.fetchone()

    if existing_ticket:
        # If ticket is in the basket, update the quantity
        eventUserTicketQuantity = existing_ticket[2] - 1
        #If statement to check whether the user still has at least 1 ticket in basket.
        if eventUserTicketQuantity > 0:
            # Update the quantity in the basket
            cursor.execute('UPDATE baskets SET quantity = ? WHERE eventID = ? AND userID = ?', (eventUserTicketQuantity, eventID, userID))
            conn.commit()
        else:
            # Remove the ticket from the basket if the quantity is zero
            cursor.execute('DELETE FROM baskets WHERE userID = ? AND eventID = ?', (str(userID), str(eventID)))
            conn.commit()

        # Increase the event ticket quantity since the ticket is being removed from the basket
        cursor.execute('UPDATE events SET eventTicketQuantity = eventTicketQuantity + 1 WHERE eventID = ?', (eventID,))
        conn.commit()

        # Commit changes before calling ShowBasket function
        conn.commit()

        # Update the display
        ShowBasket()
        
def ScanQRCode(oldMainPage = None):
    # Opens a file dialog to select a QR code image.
    QRData = filedialog.askopenfilename(initialdir=os.path.join(os.getcwd(), 'qrcodes'), title="Select a QR Code", filetypes=[("Image files", "*.png")])
    
    # Checks if a QR code image is selected.
    if QRData:
        try:
            # Reads the QR Code 
            image = cv2.imread(QRData)
            detector = cv2.QRCodeDetector()
            # Checks for four values below
            retval, decoded_info, points, straight_qrcode = detector.detectAndDecodeMulti(image)

            # If retval present (boolean to indicate whether QR code was detected) continue
            if retval:
                # Extracts eventID from the decoded information.
                eventID = decoded_info[0]
                
                #Queries database to select event
                cursor.execute('SELECT eventID FROM events WHERE eventID = ?', eventID)
                event_details = cursor.fetchone()

                # Check if the evnet with the given ID is found.
                if event_details:
                    # Displays the event details of the provided eventID.
                    showEventDetails(event_details, oldMainPage)
                #Display error message if event not found
                else:
                    messagebox.showinfo('Error', 'Event not found')
            #Display error message if no QR Code is detected in the image.
            else:
                messagebox.showinfo('Error', 'No QR code found in the image')
       #Error handling of any exeception
        except Exception as e:
            messagebox.showinfo('Error', f'Error processing QR Code: {str(e)}')


def LogIn(username='', password='', oldPage=False):
    # Checks if both username and pasword are provided.
    if username != '' and password != '':
        # Retrieves password and userID from the database for the given username.
        cursor.execute('SELECT password, userID FROM users WHERE username=?', [username])
        user = cursor.fetchone()
        
        # Checks if the user exists and the password is correct.
        if user is None or not bcrypt.checkpw(password.encode('utf-8'), user[0]):
            messagebox.showerror('Error.', 'Invalid credentials.')
        else:
            # Sets userID variable to global variable and navigates user to main page.
            global currentUserID
            currentUserID = user[1]
            showMainPage(oldPage)
    # Displays error message if username and password are not entered into.
    else:
        messagebox.showerror('Error', 'Please enter both username and password.')
    

def create_account(username='', password='', email='', dob='', oldPage=False):

    # Defines regular expression patterns for username, password and email.
    # Username can be alphanumeric. Passwords must be 3 characters long or more
    username_pattern = re.compile(r'^[a-zA-Z0-9]{3,}$') 
    
    # Password can be alphanumeric and contain special characters. Password must be 7 characters or more.
    password_pattern = re.compile(r'^[a-zA-Z0-9!@#$%^&*()_+{}\[\]:;<>,.?~\\-]{7,}$')
    
    # Email can be alphanumeric, and contain dots, underscores and hyphens. 
    email_pattern = re.compile(r'^[a-zA-Z0-9._-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}$')

    # Date of Birth pattern in DD/MM/YYYY format with valid ranges for day and month.
    dob_pattern = re.compile(r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$')

    # Dictionary list to store error messages
    error_messages = []
    
    # Validate username using regular expression pattern.
    if not username_pattern.match(username):
        error_messages.append('Username must be 5 characters (alphanumeric).')

    # Validate password using regular expression pattern.
    if not password_pattern.match(password):
        error_messages.append('Password must be 7 characters and contain a number.')

    # Validate email using regular expression pattern.
    if not email_pattern.match(email):
        error_messages.append('Email must be a valid email address.')

    
    if dob != '':
        # Validate date of birth using regular expression pattern.
        if not dob_pattern.match(dob):
            error_messages.append('Date of Birth must be in DD/MM/YYYY format.')
        # If date of birth is provided, check if it matches the specified format and user is 18 years old or older.
        else:
            birth_date = datetime.strptime(dob, "%d/%m/%Y")
            today = datetime.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

            # If user is less than 18 years of age, deny access and display error message.
            if age < 18:
                error_messages.append('You must be 18 or older to create an account.')

    # If there are error messages, display them in an error message.
    if error_messages:
        messagebox.showerror('Error', '\n'.join(error_messages))
    else:
        # Encode and hash the password using bcrypt.
        encoded_password = password.encode('utf-8')
        hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt(rounds=12))
        
        # Insert the user information into the users database table.
        cursor.execute('INSERT INTO users (username, password, email, dob) VALUES (?, ?, ?, ?)', [username, hashed_password, email, dob])
        conn.commit()
        
        # Display a success message and navigate to the main page.
        messagebox.showinfo('Success', 'Account has been created.')
        showLoginPage(oldPage)

# SQLite Database
try:
    conn = sqlite3.connect('test.db') #Title of database
    cursor = conn.cursor() #Establish connection to database
    #Create users table with constraints
    cursor.execute('''        
    CREATE TABLE IF NOT EXISTS users (
        userID INTEGER PRIMARY KEY AUTOINCREMENT, 
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        email TEXT NOT NULL,
        dob TEXT NOT NULL
    )
    ''')
    #Create events table with constraints 
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        eventID INTEGER PRIMARY KEY AUTOINCREMENT,
        userID INTEGER,
        eventName TEXT NOT NULL,
        eventDay INTEGER NOT NULL,
        eventMonth INTEGER NOT NULL,
        eventVenue TEXT NOT NULL,
        eventAddress TEXT NOT NULL,
        eventGenre TEXT NOT NULL,
        eventTicketPrice FLOAT NOT NULL,
        eventDescription TEXT NOT NULL,
        eventImage BLOB,
        qrCode BLOB,
        eventTicketQuantity INTEGER NOT NULL,
        eventPromotionDiscount INTEGER,
        FOREIGN KEY(userID) REFERENCES users(userID)
     )
    ''')
    
    # Unique constraints used below to prevent duplicate entries for the same user and event.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS baskets (
        userID INTEGER,
        eventID INTEGER,
        quantity INTEGER,
        totalPrice FLOAT,
        CONSTRAINT unq_user_event UNIQUE(userID, eventID),
        FOREIGN KEY(userID) REFERENCES users(userID),
        FOREIGN KEY(eventID) REFERENCES events(eventID) 
    )
    ''') 
    # Currently this table isn't used, but could be used to see which users clicked on which events (can be added from ShowEventDetails)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS interactions (
        userID INTEGER,
        eventID INTEGER,
        CONSTRAINT unq_user_event UNIQUE(userID, eventID),  
        FOREIGN KEY(userID) REFERENCES users(userID),
        FOREIGN KEY(eventID) REFERENCES events(eventID) 
    )
    ''') 
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS favourites (
        userID INTEGER,
        eventID INTEGER,
        CONSTRAINT unq_user_event UNIQUE(userID, eventID),
        FOREIGN KEY(userID) REFERENCES users(userID),
        FOREIGN KEY(eventID) REFERENCES events(eventID) 
    )
    ''')

# Exception catcher for any errors that may occur during the execution of SQL commands. 
except sqlite3.Error as e:
    print(f"Database error: {e}")

        
# Call showLoginPage function so that when application is launched, the Log in page is displayed first. 
showLoginPage()
app.mainloop()

