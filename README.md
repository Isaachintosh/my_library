# my_library

## Welcome to my Odoo Module App

# Pre requisites

First of all, you need these technologies to run this module:

- Python 3 or above installed in your Virtual Environment

- An Odoo Instance pre-configured with an Virtual Environment activated

- Obs.: For this module I used a Virtual Environment named "odoo-12.0"

- A file .cfg into the odoo-dev/odoo with the name of the instance

# How to run

- First of all, clone this repository at the local-addons folder inside the odoo-dev folder

- After that you will initiate the venv of the instance, for example:

Terminal command: 
    
    source ~/odoo-12.0/bin/activate

- And now you initialize the Odoo Server with the following command:
    
Terminal command:

    odoo/odoo-bin --addons-path=odoo/addons,local-addons/

Also if you want to see the server executing the debug checks during live, you could add "--log-level=debug" to the command.

Terminal command with live debug activated

    odoo/odoo-bin --addons-path=odoo/addons,local-addons/ --log-level=debug

# How to check if the module has been load succesfully:

- Check if the server log of the terminal had run the instance and initiated the services with http statuses 200, if not, the terminal will show the error.

- Access the Odoo instance UI with admin login credentials

- Navigate to the Apps section

- Remove the apps filter

- type in the search box:

        my_library
    
- If the module has been found, click at the install button, also you can check if the installation of the module is running.

- As soon as it finishes the installation, Odoo will refresh the page to access the module's UI.

- Finally, try to register a book, considering that you must activate the session's super-user mode.

# If you encounter any problem at the module execution, what you can do?

- You can create an issue here in the repository and I gonna see what happened.

- You can you send me an email with the subject "my_module issue".

For both options I will respond as soon as possible with pleasure to learn and help in learning the framework.