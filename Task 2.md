Task 2: Single user web app

Authorize this user by logging in from google (or just normal login, ehichever is easier), with an pre-allowed gmail email.

Functionalities:

1. User should be able to enter a video url, or video id, and it will show the video title and channel name.
1a. If it's in the database fetch from there, if not run an api call and add it to the existing table.

2. User should be able to write a markdown note for this video, using the TipTap editor that's currently implemented in frontend
2a. This is stored in a different table, which also has the PK video_id. If the video_id user entered already has a note, load that to the TipTap editor when executing 1.
2b. For now, don't auto save and just keep a save button. On clicking, it should update the table entry.
2c. Table entry should be in markdown.

3. There is only one user, and these functionalities should be accessible from the next js frontend when logged in from an authorized gmail or email.