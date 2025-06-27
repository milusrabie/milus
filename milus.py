from seleniumbase import SB
import time
import requests

def is_twitch_live(username: str) -> bool:
    """Check if a Twitch stream is currently live."""
    url = f"https://www.twitch.tv/{username}"
    headers = {
        "Client-ID": "kimne78kx3ncx6brgo4mv6wki5h1ko",  # Publicly known
    }
    try:
        response = requests.get(url, headers=headers)
        return "isLiveBroadcast" in response.text
    except requests.RequestException as e:
        print(f"[Error] Failed to check stream status: {e}")
        return False

def handle_captcha(sb: SB):
    """Attempt to solve GUI CAPTCHA using seleniumbase utils."""
    sb.uc_gui_click_captcha()
    sb.sleep(1)
    sb.uc_gui_handle_captcha()
    sb.sleep(1)

def accept_consent(sb: SB):
    """Click the 'Accept' button if present."""
    if sb.is_element_present('button:contains("Accept")'):
        sb.uc_click('button:contains("Accept")', reconnect_time=4)

def monitor_stream(sb: SB, url: str, check_element: str):
    """Open stream in new driver and monitor the presence of a key element."""
    driver = sb.get_new_driver(undetectable=True)
    driver.uc_open_with_reconnect(url, 5)
    handle_captcha(driver)
    accept_consent(driver)

    print(f"[Info] Monitoring stream at {url} ...")
    while is_twitch_live("brutalles"):
        sb.sleep(10)
    sb.quit_extra_driver()

def handle_kick_stream(sb: SB, username: str):
    url = f"https://kick.com/{username}"
    sb.uc_open_with_reconnect(url, 5)
    handle_captcha(sb)
    accept_consent(sb)

    if sb.is_element_visible('#injected-channel-player'):
        monitor_stream(sb, url, check_element='#injected-channel-player')

def handle_twitch_stream(sb: SB, username: str):
    if not is_twitch_live(username):
        print(f"[Info] Twitch user '{username}' is offline.")
        return

    url = f"https://www.twitch.tv/{username}"
    sb.uc_open_with_reconnect(url, 5)
    accept_consent(sb)

    chat_selector = 'div[aria-label="Chat messages"]'
    monitor_stream(sb, url, check_element=chat_selector)

def main():
    twitch_user = "brutalles"
    kick_user = "brutalles"

    with SB(uc=True, test=True) as sb:
        handle_kick_stream(sb, kick_user)
        sb.sleep(1)
        handle_twitch_stream(sb, twitch_user)
        sb.sleep(1)

if __name__ == "__main__":
    main()
