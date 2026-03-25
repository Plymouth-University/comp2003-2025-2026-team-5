<?php

session_start();

session_destroy();

header("Location: /geofence/src/sign_in_page.html");