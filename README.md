SpotifyNoHands
==============

A Twilio SMS server that will accept an artist name and look it up using The Echo Nest and Spotify APIs. 
It will respond with a text that contains a URL to a song by the artist.

Details
=======
I like to listen to post-rock. Unfortunately, post-rock bands tend to have very long names like ‘Explosions in the Sky’, ‘God Speed you black
emperor’, and ‘This will Destroy You’.  I have a long commute and I will find that I am frequently risking my life trying to type a long band name
into my music player.  I wish Siri supported non-itunes players like Spotify, but until then I need a way to tell Spotify to play music by bands
with long names. If I don’t, I will die in a fiery crash on Route 3 in Lowell Mass. A horrible way to go.   So this weekend at the Artists Hack I
built something to solve this problem. It lets you play music in Spotify without having to type long artist names. Here’s how it works.

I used Twilio to set up a phone number such that if you text it an artist name, it will respond with a spotify link to a song by that artist.  You
can add the phone number to your contacts as “music player”,  You can then use Siri  in a dialog like so:

    Me: Send a text to Music Player

    Siri: What would you like it to say

    Me: Explosion in the Sky

    Siri: OK, I’ll send it

A few seconds later I get a text message back with a link to a popular track by Explosions in the Sky. I tap the link and Spotify opens and plays
the song.  It is about as simple a hack, but it solves a real problem for me.  
