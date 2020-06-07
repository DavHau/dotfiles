weather = hass.states.get("weather.openweathermap")
forecast = weather.attributes["forecast"]
notified_today = hass.states.get("input_boolean.rain_notified_today")


def format_time(time):
    return f"{time.hour:02}:{time.minute:02}"


def main():
    if notified_today.state == "on":
        return

    now = datetime.datetime.now()
    rain_start = None
    rain_times = []
    for entry in forecast:
        time = datetime.datetime.fromtimestamp(entry["datetime"] / 1000)
        # in the past
        if time < now:
            continue
        # limit to the same day
        if time.day != now.day:
            break

        if entry["condition"] == "rainy":
            if rain_start is None:
                logger.info(f"rain starts at {time}")
                rain_start = time
        elif rain_start is not None:
            logger.info(f"rain ends at {time}")
            rain_times.append((rain_start, time))
            rain_start = None

    if rain_start is not None:
        rain_times.append((rain_start, time))

    if not rain_times:
        return

    ranges = []
    for time in rain_times:
        logger.info(f"rain_time: {time[0]} -> {time[1]}")
        ranges.append(f"{format_time(time[0])}→{format_time(time[1])}")
    message = f"There is rain predicted today: {', '.join(ranges)}"

    hass.services.call("notify", "pushover", {"message": message}, blocking=False)
    hass.services.call("notify", "mobile_app_beatrice", {"message": message}, blocking=False)

    hass.services.call("input_boolean", "turn_on",
            {"entity_id": "input_boolean.rain_notified_today"},
            blocking=False)

main()
