#i am not trying to validate staff from sites, i am only using
#regexes to recognize fields

REGEX_NAME = '^([A-Za-z\'\s]+)$'
REGEX_EMAIL = '^(@[a-z.]+)$'
REGEX_POSITION = '^([A-Za-z\s,\']+)$'
REGEX_PHONE = '^([0-9()\s-]+)$'