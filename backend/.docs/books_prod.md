A second table has been added to .env, as SUPABASE_URL_2

Task:

Implement a way for users to add books to this database, similar to how youtube videos are added in the other database
Instead of YT DLP, user will upload a direct json containing book chapters titles and chapter text (this stored in a backet on 2nd database)
- This should mirror youtube video chunk title and chunk text

Also instead of YT data api v3, users will manually enter the properties of a book like title, author, etc when adding the json

The page for viewing chapters, and taking notes, will be identical to how it's implemented in youtube subtitle chunks.
Reuse as much code and components as possible to aboid repetition.

Make sure that all book related things will be stored in the 2nd database

(user login should not be touched, that's still in the main database, and that's the same authorization used to access the books from frontend)

instead of video_id, books will have a book_id that's a short sting user enters upon uploading the json, and it will show up on the route as books/b?=the_subtle_art