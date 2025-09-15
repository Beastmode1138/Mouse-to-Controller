# Author: Aryan Kainth
# controllerMouse.py
# 2025-05-07
#
# Simple Mouse to Controller Mapping
#
# ===================================================================
import pygame
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
import time
import platform
import sys
import traceback
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
# import threading # We will not use threading for the tkinter window with this approach

# Initialize Pygame
pygame.init()
pygame.joystick.init()

# Initialize controllers
mouse = MouseController()
keyboard = KeyboardController()

# --- Configuration ---
# Adjust these values to change mouse sensitivity
MOUSE_SPEED = 15

# Button mappings (common for Xbox controllers in pygame)
BUTTON_A = 0  #Left click
BUTTON_B = 1  #Right Click
BUTTON_LB = 4 #Back Button (Mouse 4)
BUTTON_RB = 5 #Forward Button   (Mouse 5)
BUTTON_START = 7  # Start button
BUTTON_Y = 3    # Y button

# Hat mappings (Arrow controls)
HAT_DPAD = 0

# --- State variables ---
# We'll keep this, but it won't affect D-pad or Y button functionality anymore
osk_open = False # Track if the On-Screen Keyboard is considered open

# --- tkinter Root and Variables ---
# Create the root tkinter window here, it's needed for variables and message boxes
root = tk.Tk()
root.withdraw() # Hide the main tkinter window

# Use a tkinter DoubleVar for the deadzone so it can be easily shared and updated
deadzone_var = tk.DoubleVar(value=0.1)


# --- Function to create the adjustment window ---
def create_adjustment_window():
    # Create a new top-level window for the adjustment controls
    # It is automatically associated with the hidden root
    adjustment_window = tk.Toplevel(root)
    adjustment_window.title("Deadzone Adjustment")
    adjustment_window.geometry("250x100")
    adjustment_window.resizable(False, False)

    # Label to display the current deadzone value
    deadzone_label = ttk.Label(adjustment_window, text=f"Current Deadzone: {deadzone_var.get():.2f}")
    deadzone_label.pack(pady=5)

    # Function to update the label text when deadzone_var changes
    def update_label(*args):
        deadzone_label.config(text=f"Current Deadzone: {deadzone_var.get():.2f}")

    # Trace changes to the deadzone_var to automatically update the label
    deadzone_var.trace_add("write", update_label)

    # Frame to hold the buttons
    button_frame = ttk.Frame(adjustment_window)
    button_frame.pack(pady=5)

    # Increase button
    def increase_deadzone():
        current_deadzone = deadzone_var.get()
        new_deadzone = round(current_deadzone + 0.01, 2)
        if new_deadzone <= 0.5: # Cap the maximum deadzone at 0.5
            deadzone_var.set(new_deadzone)
            print(f"Deadzone increased to: {deadzone_var.get():.2f}")


    increase_button = ttk.Button(button_frame, text="Increase (+0.01)", command=increase_deadzone)
    increase_button.grid(row=0, column=0, padx=5)

    # Decrease button
    def decrease_deadzone():
        current_deadzone = deadzone_var.get()
        new_deadzone = round(current_deadzone - 0.01, 2)
        if new_deadzone >= 0.0: # Prevent deadzone from going below 0
            deadzone_var.set(new_deadzone)
            print(f"Deadzone decreased to: {deadzone_var.get():.2f}")


    decrease_button = ttk.Button(button_frame, text="Decrease (-0.01)", command=decrease_deadzone)
    decrease_button.grid(row=0, column=1, padx=5)

    # Protocol handler for when the window is closed
    # When the adjustment window is closed, we should ideally also stop the main loop
    def on_closing_adjustment_window():
        print("Adjustment window closed. Exiting program.")
        global running # Access the running variable in the global scope
        running = False
        adjustment_window.destroy() # Destroy the adjustment window


    adjustment_window.protocol("WM_DELETE_WINDOW", on_closing_adjustment_window)


# --- Controller Detection Loop ---
controller = None
print("Searching for Xbox One controller...")

while controller is None:
    joystick_count = pygame.joystick.get_count()

    if joystick_count == 0:
        # No joystick detected, show pop-up
        response = messagebox.askretrycancel(
            "Controller Not Found",
            "No Xbox One controller detected. Please ensure it is connected.\n\nDo you want to try detecting again?"
        )

        if response: # User clicked Retry
            print("Attempting to detect controller again...")
            # Continue the while loop
        else: # User clicked Cancel
            print("User cancelled. Exiting program.")
            pygame.quit()
            root.destroy() # Destroy the tkinter root window
            sys.exit() # Exit the program

    else:
        # Controller found
        controller = pygame.joystick.Joystick(0)
        controller.init()
        print(f"Detected joystick: {controller.get_name()}")
        print(f"Number of buttons: {controller.get_numbuttons()}")
        print(f"Number of hats: {controller.get_numhats()}")

# --- Create the adjustment window (in the main thread) ---
create_adjustment_window()

# --- Main loop (This will run in the main thread) ---
running = True
try:
    while running:
        # Handle pygame events
        for event in pygame.event.get():
            # --- Debugging Prints for Joystick Events (Removed) ---
            # if event.type in [pygame.JOYAXISMOTION, pygame.JOYBALLMOTION, pygame.JOYBUTTONDOWN,
            #                   pygame.JOYBUTTONUP, pygame.JOYHATMOTION]:
            #     print(f"Joystick Event: Type={event.type}, Button/Axis/Hat={getattr(event, 'button', getattr(event, 'axis', getattr(event, 'hat', 'N/A')))}, Value={getattr(event, 'value', 'N/A')}")
            # --- End Debugging Prints ---

            if event.type == pygame.QUIT:
                running = False

            # Handle button presses
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == BUTTON_A:
                    print("A pressed: Simulating left click")
                    mouse.press(Button.left)
                elif event.button == BUTTON_B:
                    print("B pressed: Simulating right click")
                    mouse.press(Button.right)
                elif event.button == BUTTON_LB:
                    print("LB pressed: Simulating Alt + Left Arrow (Back)")
                    with keyboard.pressed(Key.alt):
                        keyboard.press(Key.left)
                        keyboard.release(Key.left)
                elif event.button == BUTTON_RB:
                    print("RB pressed: Simulating Alt + Right Arrow (Forward)")
                    with keyboard.pressed(Key.alt):
                        keyboard.press(Key.right)
                        keyboard.release(Key.right)
                elif event.button == BUTTON_START:
                    print("Start pressed: Toggling On-Screen Keyboard (Win + Ctrl + O)")
                    try:
                        # Simulate Windows Key + Ctrl + O
                        with keyboard.pressed(Key.cmd):
                            with keyboard.pressed(Key.ctrl):
                                keyboard.press('o')
                                keyboard.release('o')
                        osk_open = not osk_open # Toggle OSK state (for tracking, no longer affects D-pad/Y)
                        print(f"OSK state: {'Open' if osk_open else 'Closed'}")
                    except Exception as e:
                        print(f"Error simulating OSK toggle: {e}")
                        traceback.print_exc()
                elif event.button == BUTTON_Y:
                    # This will now always simulate Enter when Y is pressed
                    print("Y pressed: Simulating Enter")
                    keyboard.press(Key.enter)
                    keyboard.release(Key.enter)


            # Handle button releases
            if event.type == pygame.JOYBUTTONUP:
                if event.button == BUTTON_A:
                    print("A released: Releasing left click")
                    mouse.release(Button.left)
                elif event.button == BUTTON_B:
                    mouse.release(Button.right)
                # No release needed for LB, RB, Start, or Y


            # Handle D-pad motion
            if event.type == pygame.JOYHATMOTION:
                if event.hat == HAT_DPAD: # Removed the 'and osk_open' condition
                    hat_x, hat_y = event.value
                    # print(f"D-pad motion: ({hat_x}, {hat_y})") # Optional: uncomment for detailed D-pad output
                    if hat_x == -1:
                        print("D-pad Left: Simulating Left Arrow")
                        keyboard.press(Key.left)
                        keyboard.release(Key.left)
                    elif hat_x == 1:
                        print("D-pad Right: Simulating Right Arrow")
                        keyboard.press(Key.right)
                        keyboard.release(Key.right)
                    if hat_y == 1:
                        print("D-pad Up: Simulating Up Arrow")
                        keyboard.press(Key.up)
                        keyboard.release(Key.up)
                    elif hat_y == -1:
                        print("D-pad Down: Simulating Down Arrow")
                        keyboard.press(Key.down)
                        keyboard.release(Key.down)


        # Get left analog stick axes (axis 0 for X, axis 1 for Y)
        # Mouse movement is always active, regardless of OSK state
        left_stick_x = controller.get_axis(0)
        left_stick_y = controller.get_axis(1)

        # Apply deadzone - get the current value from the tkinter variable
        current_deadzone = deadzone_var.get()
        if abs(left_stick_x) < current_deadzone:
            left_stick_x = 0
        if abs(left_stick_y) < current_deadzone:
            left_stick_y = 0

        # Calculate mouse movement
        move_x = left_stick_x * MOUSE_SPEED
        move_y = left_stick_y * MOUSE_SPEED

        # Move the mouse
        if move_x != 0 or move_y != 0: # Only move if there's significant stick movement
             mouse.move(move_x, move_y)

        # --- Process tkinter events ---
        try:
            root.update_idletasks()
            root.update()
        except tk.TclError:
            # This can happen if the tkinter window is closed
            running = False # Stop the main loop if tkinter errors out

        # Small delay to prevent the loop from consuming too much CPU
        time.sleep(0.01)

except Exception as e:
    print(f"\nAn unhandled error occurred during the main loop: {e}")
    traceback.print_exc()

finally:
    pygame.quit()
    root.destroy() # Ensure tkinter window is also destroyed on exit
    print("Program terminated.")
