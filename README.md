# Mastodon bot: RSS
## Script origin
This script initialy comes from [www.bentasker.co.uk](https://www.bentasker.co.uk/posts/blog/software-development/writing-a-simple-mastodon-bot-to-submit-rss-items.html)

Some changes have been made in order to use YAML instead of JSON for the feed list,
and the feed listing now allows to pass some more data, such as "sensitive" for
content-warning tag (which would apply to the whole feed), and custom, static tags.

## Parameters
The following parameters are supported, and should passed as environment variables.

### HASH_DIR
Set the hash directory. String. Defaults to ```/hashdir```

### INCLUDE_AUTHOR
Display entry author or not. Boolean. Defaults to ```True```

### CW_TAG
For feed using tags, allows to switch the "content warning" flag for the post entry if this
CW_TAG is set. String. Defaults to ```content-warning```

### MASTODON_URL
Set the Mastodon instance URL. String. Defaults to ```https://mastodon.social```

### MASTODON_TOKEN
Set the mastodon authentication token. String. Mandatory.

### MASTODON_VISIBILITY
Set the visibility of the content. String. Defaults to ```public```

### DRY_RUN
Toggle mode - if yet to ```Y``` will not actually send data to mastodon, but output what would
have been sent. Char. Defaults to ```N```

### SKIP_TAGS
For feed using tags, allow to not show the specified tags. Coma separated value.

### LAST_ENTRIES
Sets the maximal amount of entries to show. Integer. Defaults to ```10```

## Running
### Building the container
```Bash
buildah bud --format docker -f Dockerfile -t mastobot:latest .
```

### Running the container in test mode
```Bash
mkdir -p hashdir
podman  run --rm \
    -e MASTODON_TOKEN="<token>" \
    -e MASTODON_URL="https://mastodon.bentasker.co.uk" \
    -v $PWD/feeds.yaml:/app/feeds.yaml:Z,ro \
    -v $PWD/hashdir:/hashdir:Z \
    -e DRY_RUN="Y" \
    mastobot:latest
```

### Actually run the bot
```Bash
mkdir -p hashdir
podman  run --rm \
    -e MASTODON_TOKEN="<token>" \
    -e MASTODON_URL="https://mastodon.bentasker.co.uk" \
    -v $PWD/feeds.yaml:/app/feeds.yaml:Z,ro \
    -v $PWD/hashdir:/hashdir:Z \
    -e DRY_RUN="N" \
    mastobot:latest
```

### SELinux
If you're running as a standard user, in your home directory, you may face some
SELinux denials. In order to sort this out, you can pass the following option to
podman:

```Bash
--security-opt label=disable
```

Also, if you want to run multiple bots using the same hashdir (not a good idea, but..), you will
need to modify the command and replace the ```Z``` by a ```z``` on the volume.

## License
[Released under BSD 3 Clause](https://www.bentasker.co.uk/pages/licenses/bsd-3-clause.html)

