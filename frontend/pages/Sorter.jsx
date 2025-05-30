/* eslint-disable react-hooks/exhaustive-deps */
/* eslint-disable no-unused-vars */
import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useSelectedPlaylistConstext } from "../src/contexts";
import spotifyLogo from '../src/assets/Spotify_icon.svg'
import "../css/main.css";
import "../css/Sorter.css";


async function play_song(songId) {
  const response = await fetch(`http://127.0.0.1:5000/playback/` + songId + '/' + 0)
  if (response.status === 200) {
    let data = await response.json();
    if (!data.success) {
      alert(data.message)
    }
  }
}


async function play_song_min(songId) {
  const response = await fetch(`http://127.0.0.1:5000/playback/` + songId + '/' + 60000)
  if (response.status === 200) {
    let data = await response.json();
    if (!data.success) {
      alert(data.message)
    }
  }
}


async function history_clear() {
  const response = await fetch(`http://127.0.0.1:5000/history/clear`)
  if (response.status !== 200) {
    alert("Connection problems")
  }
}


function PlaylistSongCard ({song}) {
  return <div className="sorter-playlist-song">
    <div className="sorter-playlist-song-nr" >
      <p>{song.nr + 1}</p>
    </div>
    <div className="sorter-playlist-song-img">
      <img src={song.image_url} alt={song.name} />
    </div>
    <div className="sorter-playlist-song-info">
      <h3>{song.artist} - {song.name}</h3>
    </div>
  </div>
}


function Sorter() {
  const [songLeft, setSongLeft] = useState({})
  const [songRight, setSongRight] = useState({})
  const [playlistName, setPlaylistName] = useState("Loading")
  const [playlistLen, setPlaylistLen] = useState(-1)
  const [localSongs, setLocalSongs] = useState(-1)
  const [progress, setProgress] = useState(0)
  const [loading, setLoading] = useState(false);
  const {playlistId, selectPlaylist, songs, setSongs} = useSelectedPlaylistConstext()

  const getSongs = async () => {
    const options = { method: "GET" }
    //@app.route("/get_songs/<playlist_id>/<reversed>/<start>/<stop>/")
    const response = await fetch(`http://127.0.0.1:5000/get_songs/` + playlistId + '/' + 0 + '/' + 0 + '/' + 0)
    if (response.status === 200) {
      let data = await response.json();
      setSongs(data.songs)
      setPlaylistName(data.name)
      setSongLeft(data.song_left)
      setSongRight(data.song_right)
      setLocalSongs(data.local_songs)
      setPlaylistLen(data.playlist_len)
      setPlaylistName(data.playlist_name)
    } 
    else {
      setPlaylistName("Cannot connect to backend")
      setSongLeft({ 'name': "Cannot connect to backend" })
      setSongRight({ 'name': "Cannot connect to backend" })
    }
    setLoading(false)
  }
      
  useEffect(() => {
    setLoading(true)
    getSongs(playlistId);
  }, [])


  function SelectCard({song}) {
      async function remove_button_func(songId) {
        const response = await fetch(`http://127.0.0.1:5000/sorter/remove/` + songId)
        if (response.status === 200) {
          let data = await response.json();
          if (data.success){
            setLoading(true)
            //setSongLeft({'name': 'Loading...'})
            //setSongRight({'name': 'Loading...'})
            setSongs(data.songs)
            setSongLeft(data.song_left)
            setSongRight(data.song_right)
            if (data.finished === true){
              setSongLeft({'name': 'SORTED :D', 'image_url': song.image_url})
              setSongRight({'name': 'SORTED :D', 'image_url': song.image_url})     // You can call it a bug, I call it feature
              alert(data.message)
            }
            setLoading(false)
          }
          else{
            alert(data.message)
          }
        }
      }


      async function selectSong(songId) {
        //setSongLeft({'name': 'Loading...', 'image_url': song.image_url})
        //setSongRight({'name': 'Loading...', 'image_url': song.image_url})     // You can call it a bug, I call it feature
        const response = await fetch(`http://127.0.0.1:5000/sorter/select/` + songId)
        if (response.status === 200) {
          let data = await response.json();
          setLoading(true)
          setSongLeft(data.song_left)
          setSongRight(data.song_right)
          setProgress(data.estimated_progress)
          setSongs(data.songs)
          if (data.finished === true){
            setSongLeft({'name': 'SORTED :D', 'image_url': song.image_url})
            setSongRight({'name': 'SORTED :D', 'image_url': song.image_url})     // You can call it a bug, I call it feature
            alert(data.message)
          }
          setLoading(false)
        }
        else{
          alert("Lost connection to backend!")
        }
  }

  return <div className="select-song">
    <div className="select-song-img">
      <img src={song.image_url} alt={song.name} />
    </div>
    <div className="select-song-info">
      {loading ? (
        <h2>Loading...</h2>
      ) : (
      <h2>{song.name}</h2>)}
      {loading ? (
        <h3>Loading...</h3>
      ) : (
      <h3>{song.artist}</h3>)}
      <></>
      <div className="select-song-button-select">
        <button onClick={() => (selectSong(song.id))}>
            Select
        </button>
      </div>
      <p></p>
      <button onClick={() => (play_song(song.id))}>
          &#9658; Play 
      </button>
      <> </>
      <button onClick={() => (play_song_min(song.id))}>
          &#9658; Play middle
      </button>
      <> </>
      <button onClick={() => (fetch(`http://127.0.0.1:5000/playback/stop`))}>
          &#9208;
      </button>
      <h2></h2>
      <div className="select-song-button-remove">
        <button onClick={() => (remove_button_func(song.id))}>
            Remove from playlist
        </button>
      </div>
      <p></p>
      <div className="select-song-button-remove-history">
        <button onClick={() => (fetch(`http://127.0.0.1:5000/sorter/remove_from_selection_history/` + song.id))}>
            Resort: Remove saved choices
        </button>
      </div>
    </div>
  </div>
  }


  

  return <>
  <div className="sorter-page">
    <div className="left-panel">
      {loading ? (
        <h2>Loading...</h2>
      ) : (
      <div className="sorter-playlist">
        {songs.map((song) => (<PlaylistSongCard key={song.id} song={song} />))}
      </div>
      )}
    </div>



    <div className="main-panel">
      <div className="test-buttons">
        <> </>
        <Link to="/" className="nav-link">
          <button> Home </button>
        </Link>
        <> </>
        <button onClick={() => (history_clear())}> Clear all choices </button>
        <> </>        
        <Link to="/" className="nav-link">
          <button onClick={() => (fetch(`http://127.0.0.1:5000/sorter/shuffle/` + playlistId))}>
             Shuffle playlist
          </button>
        </Link>
        <> </>        
        <Link to="/" className="nav-link">
          <button onClick={() => (fetch(`http://127.0.0.1:5000/sorter/reverse/` + playlistId ))}>
             Reverse playlist
          </button>
        </Link>
        <> </>        
        <Link to="/" className="nav-link">
          <button onClick={() => (fetch(`http://127.0.0.1:5000/sorter/reorder` ))}>
             Update order to Spotify
          </button>
        </Link>
      </div>
      <h2>Select song you like more:</h2>
      <div className="select-main">
        <SelectCard song={songLeft}></SelectCard>
        <div className="select-spacer"></div>
        <SelectCard song={songRight}></SelectCard>
      </div>
    </div>



    <div className="right-panel">
      <div className="right-panel-home-logos">
        <a href="https://www.youtube.com/watch?v=7WF0KGtiETU" target="_blank">
          <img src={spotifyLogo} className="logo spotify" alt="Spotify logo" width="64" height="64"/>
        </a>
      </div>
      <h2>Playlist info:</h2>
      <h3>{playlistName}</h3>
      <p>{playlistLen} Songs</p>
      <h3></h3>
      <p>Estimated progress:</p>
      <h3>{progress.toFixed(3)} %</h3>
      <h2>Debug</h2>
      <p>Playlist ID:</p>
      <p>{playlistId}</p>
      <h5></h5>
      <p># local songs: {localSongs}</p>
      <p style={{color: "red"}}>Local songs are sortable! Somehow.</p>
      <p>*Cannot remove local songs yet!</p>
    </div>
  </div>
  </>
}

export default Sorter;
