# discord-bot

<a href="https://github.com/psf/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style: Black">
</a>
<a href="https://www.python.org/downloads/">
    <img alt="Python Version" src="https://img.shields.io/badge/python-3.10%2B-blue">
</a>
<a href="https://github.com/Rapptz/discord.py/">
    <img src="https://img.shields.io/badge/discord-py-blue.svg" alt="discord.py">
</a>
<br></br>

1. [About](#about)
1. [Installation](#installation)
1. [License](#license)

Check out the [discord.py Documentation](https://discordpy.readthedocs.io/en/latest/intro.html) for additional information if not using docker.

## About

A simple Discord bot with a set of utility and moderation tools.

**Current Features:**

- Slash commands
- OpenAI GPT Chatbot Integration
- Set your own prefix (Default: `?`)
- Prune messages
- Server Member count channel
- JST timezone display
- User avatar fetcher
- User info fetcher
- ...More to come

## Installation

### Dependencies

Install [Python 3.10](https://www.python.org/downloads/) or above if not using docker.

Install [MariaDB](https://mariadb.org/download/) version 10.6.x or above.

Configure MariaDB for [Remote Client Access](https://mariadb.com/kb/en/configuring-mariadb-for-remote-client-access/) and/or [Local Client Access](https://www.digitalocean.com/community/tutorials/how-to-install-mariadb-on-ubuntu-18-04).

Create a table in your database with the following schema:

```
CREATE TABLE IF NOT EXISTS guilds (id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL UNIQUE, guild_name TEXT NOT NULL, guild_id BIGINT NOT NULL UNIQUE, prefix TEXT NOT NULL DEFAULT '?', member_count_channel_id BIGINT)
```

If you're using docker and need to access the database on localhost, consider adding `network_mode: "host"` to the `docker-compose.yml` file if you have trouble connecting to the database.

### Docker

1. Install [Docker](https://docs.docker.com/engine/install/) on your preferred operating system.
1. Log into your [Discord](https://discord.com/) account and open the [Discord developer portal](https://discord.com/developers/docs/getting-started#configuring-a-bot).
1. Create a [Bot account](https://discordpy.readthedocs.io/en/stable/discord.html).
1. Clone this repository.
1. Rename `.env.sample` to `.env` and add the information for your bot and database.

**Run the following commands while inside the cloned repository to build and run a docker container with this code.**

#### Linux

```
sudo docker compose build
```

```
sudo docker compose up -d
```

#### Windows

```
docker-compose build
```

```
docker-compose up -d
```

## License

Released under the [MIT](https://spdx.org/licenses/MIT.html) license.
