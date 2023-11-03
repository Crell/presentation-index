import subprocess
import shutil
import os

def run():
    lines = filter(None, [i.strip() for i in open('slides.txt', 'r') if i[0] != '#' ])
    collection = []
    for line in sorted(lines):
        [title, presentation] = line.split('|')
        collection.append((title, build(presentation)))
    build_index(collection)


def build_index(collection):
    sections = []

    confs = conference_order()
    for (presentation_title, paths) in collection:
        lines = []
        for (tag, title) in confs:
            if tag in paths:
                lines.append('<li><a href="' + paths[tag] + '/">' + title + '</a></li>\n')

        sections.extend(["""
        <section>
            <h2>{title}</h2>
            <ol>
                {section}
            </ol>
        </section>
        """.format(title = presentation_title, section = ' '.join(lines))])

    with open("web/index.html", "w") as w:
        w.write("""
    <html>
        <head>
            <title>Presentation Archive for Larry Garfield</title>
        </head>
        <body>
            <h1>Presentation Archive for Larry Garfield</h1>
            <p>This is an incomplete index of most presentation slide decks by Larry Garfield over the past few years.
            There are a few missing, either because they were not tagged properly or the presentation didn't include HTML slides.</p>
            <p>Presentations are listed alphabetically. Instances of a presentation are listed chronologically.</p>
            <p>Videos of many of these are avaiable on my <a href="https://www.youtube.com/playlist?list=PLAi1rj7b0ApWScH6njlptekH-WjohZ3zs">YouTube channel</a>.</p>
            {body}
        </body>
    </html>
    """.format(body = "\n".join(sections)))

def conference_order():
    # A static variable. I feel dirty.
    if not hasattr(conference_order, 'lookup'):
        conference_order.lookup = []
        # I'm sure there's some way to fold this entire thing into a single comprehension,
        # But I'm not sure what.
        events = filter(None, [i.strip() for i in open('events.txt', 'r') if i[0] != '#' ])
        for event in events:
            [tagname, title] = event.split('|')
            conference_order.lookup.append((tagname, title))

    return conference_order.lookup


def build(presentation_id):
    git_url = "https://github.com/Crell/" + presentation_id + ".git"
    presentation_dir = './' + presentation_id

    subprocess.call(['git', 'clone', git_url])
    tags = subprocess.check_output(['git', 'tag'], cwd=presentation_dir, encoding="ascii")

    targets = {}

    for tag in tags.strip().split("\n"):
        web_dir = os.path.join(presentation_id, tag)
        target_dir = os.path.join('web', web_dir)
        targets[tag] = web_dir
        subprocess.call(['git', 'checkout', tag], cwd=presentation_dir)
        shutil.copytree(presentation_dir, target_dir, ignore=shutil.ignore_patterns('.git*', '*.md'))
        # Possibly better alternative? Figure this out later, maybe. This line doesn't work yet.
        #subprocess.call(['git', 'archive', '--worktree-attributes', '|', 'tar', 'x'], cwd=presentation_dir)

    # Clean up
    shutil.rmtree(presentation_dir)
    return targets

# Kick off the program defined above.
run()
