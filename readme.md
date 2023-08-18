# To containerize
docker build -t content_moderator:content_moderator_1_0 .

# To run
docker run -it --env-file .env --network wa_social_api_network -v /Users/mac5/Projects/WorkoutAppsSocial/WorkoutAppsSocial.Api/wwwroot/:/mnt/data --rm content_moderator:content_moderator_1_0