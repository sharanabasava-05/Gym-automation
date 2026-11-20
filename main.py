from selenium import webdriver
from selenium.webdriver.common.by import By
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# -------------------------step1----------------------------------
# my credentials are
ACCOUNT_EMAIL = "test@gmail.com"
ACCOUNT_PASSWORD = "pass123"
#GYM url
GYM_URL = "https://appbrewery.github.io/gym/"

# setup a chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach",True)

# creates a folder for database
user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

driver = webdriver.Chrome(options=chrome_options)

wait = WebDriverWait(driver, 2)

# request the url using the driver
driver.get(GYM_URL)


# ---------------------------step2------------------------------
def retry(func, retrys=7,description=None):
    for i in range(retrys):
        print(f"trying {description}, Attempt {i+1}")
        try:
            return func()
        except TimeoutException:
            if i == retrys - 1:
                raise
            time.sleep(1)


def login():
    login_element = wait.until(EC.presence_of_element_located((By.ID, "login-button")))
    login_element.click()

    # to add the credintils for the login page
    # sending the email key
    email = wait.until(EC.presence_of_element_located((By.NAME, "email")))
    email.send_keys(ACCOUNT_EMAIL)

    # sending the password key
    password = wait.until(EC.presence_of_element_located((By.NAME, "password")))
    password.send_keys(ACCOUNT_PASSWORD)

    # submit the login button
    submit_login = wait.until(EC.presence_of_element_located((By.ID, "submit-button")))
    submit_login.click()

    wait.until(EC.presence_of_element_located((By.ID, "schedule-page")))


# use the retry functanlity for login function
def book_class(booking_button):
    booking_button.click()
    wait.until(lambda d: booking_button.text == "Booked")

retry(login,description="login")

class_cards = driver.find_elements(By.CSS_SELECTOR, ".Schedule_dayGroup__y79__")
class_booked = 0
waitlists_joined = 0
already_booked = 0

processed_info = []
MY_TIME = "6:00 PM"
# looping through all the cards days
for today in class_cards:
    # check if the current day is tuesday or sunday
    if "Tue" in today.text or "Thu" in today.text:
        # if it is any of the day then do book the current day class
        # current class holds the all the classes details
        current_class = today.find_elements(By.CLASS_NAME, "ClassCard_card__KpCx5")
        # loop through all the classes
        for class_ in current_class:
            # check the class_ matches our timing and book a class of that timing

            if MY_TIME in class_.text:
                class_type = class_.find_element(By.CLASS_NAME, "ClassCard_className__q0kVz").text
                day_date = today.find_element(By.CLASS_NAME, "Schedule_dayTitle__YBybs").text
                button = class_.find_element(By.CSS_SELECTOR, "button[id^='book-button-']")

                #--------step 4 -------check if it is booked or not to handle the exception-------
                class_info = f"{class_type} on {day_date}"
                if button.text == "Booked":
                    print(f"✓ aldready Booked {class_info}")
                    already_booked += 1
                    processed_info.append(f"[Booked] {class_info}")

                elif button.text == "Waitlisted":
                    print(f"✓ already waitlisted: {class_info}")
                    already_booked += 1
                    processed_info.append(f"[Waitlisted] {class_info}")

                elif button.text == "Book Class":
                    # use retry function
                    retry(lambda :book_class(button),description="Booking")
                    class_booked += 1
                    print(f"✓ Successfully booked: {class_info}")
                    processed_info.append(f"[New Booking] {class_info}")
                    time.sleep(0.5)

                elif button.text == "Join Waitlist":
                    # use retry function
                    retry(lambda: book_class(button), description="Waitlisting")
                    print(f"✓ Joined waitlist for: class {class_info}")
                    processed_info.append(f"[New waitlisted] {class_info}")
                    waitlists_joined += 1



# ---------stpe-7 --check my bookings and print the details--------------

# total how many classes we booked
total_class = class_booked + waitlists_joined + already_booked
print(f"Total Tuesday/Thuesday {MY_TIME} classes are : {total_class}")
print("\n--- VERIFYING ON MY BOOKINGS PAGE ---")

def get_my_bookings():
# navigate to my booking page
    booking_button = wait.until(EC.element_to_be_clickable((By.ID,"my-bookings-link")))
    booking_button.click()
    wait.until(EC.presence_of_element_located((By.ID, "my-bookings-page")))
    cards = driver.find_elements(By.CSS_SELECTOR, "div[id*='card-']")
    if not cards:
        raise TimeoutException("No booking cards found - page may not have loaded")
    return cards

all_cards = retry(get_my_bookings, description="Get my bookings")
# print the total classes

# verify the classes in my booking page
my_booking_class = driver.find_elements(By.CLASS_NAME,"MyBookings_bookingCard__VRdrR")

verified = 0
# check all the booking cards
for class_ in my_booking_class:
    try:
         # verifing the classes
        when = class_.find_element(By.CSS_SELECTOR, ".MyBookings_bookingDetails__QG0l_ p").text
        # if the class details matches our day then verify the class
        if ("Tue" in when or "Thu" in when) and f"{MY_TIME}" in when:
            class_name = class_.find_element(By.TAG_NAME, "h3").text
            print(f" ✓ verified: {class_name}")
            verified += 1
    except NoSuchElementException:
        continue
print("\n---VERIFIED DETAILS---")
if total_class == verified:
    print(f"Expected : {total_class}")
    print(f"Verified : {verified}")
    print("✅ SUCCESSFULLY VERIFIED: all the classes")
else:
    print(f"Expected : {total_class}")
    print(f"Verified : {verified}")
    print(f"❌ Mismatch found : {total_class - verified}")














