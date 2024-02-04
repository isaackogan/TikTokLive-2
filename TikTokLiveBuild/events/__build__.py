from events.transcribe import EventsTranscriber

if __name__ == '__main__':

    # Transcribe the events
    EventsTranscriber(
        template_dir="./",
        template_name="events_template.jinja2",
        output_path="../../TikTokLive/events/proto_events.py",
        merge_path="TikTokLive.events.proto_events"
    )()

