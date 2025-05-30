/* eslint-disable no-unused-vars */
import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useSelectedPlaylistConstext } from "../src/contexts";
import reactLogo from '../src/assets/react.svg'
import viteLogo from '/vite.svg'
import spotifyLogo from '../src/assets/Spotify_icon.svg'

import "../css/main.css";


function PlaylistCard({ playlist }) {
  const id = playlist.id
  const { playlistId, selectPlaylist } = useSelectedPlaylistConstext()
  return <div className="playlist-card">
    <div className="playlist-button" >
      <Link to="/Sorter" className="nav-link">
        <button onClick={() => (selectPlaylist(id))}>Select</button>
      </Link>
    </div>
    <div className="playlist-img">
      <img src={playlist.image_url} alt={playlist.name} />
    </div>
    <div className="playlist-info">
      <h3>{playlist.name}</h3>
      <p>{playlist.len} songs</p>
    </div>
  </div>
}


function Home() {
  const [loading, setLoading] = useState(false);
  const { playlists, setPlaylists } = useSelectedPlaylistConstext()
  const { playlistId, selectPlaylist } = useSelectedPlaylistConstext()

  useEffect(() => {
    const getPlaylists = async () => {
      const options = { method: "GET" }
      const response = await fetch(`http://127.0.0.1:5000/get_playlists`)
      if (response.status === 200) {
        let data = await response.json();
        setPlaylists(data.playlists)
        setLoading(false)
      } 
      else {alert("Backend not working.")}
    }

    setLoading(true)
    getPlaylists(playlistId);
  }, [playlistId, setPlaylists])


  return <>
    <div className="home-logos">
      <a href="https://vite.dev" target="_blank">
        <img src={viteLogo} className="logo" alt="Vite logo" />
      </a>
      <a href="https://react.dev" target="_blank">
        <img src={reactLogo} className="logo react" alt="React logo" />
      </a>
      <a href="https://open.spotify.com/" target="_blank">
        <img src={spotifyLogo} className="logo spotify" alt="Spotify logo" />
      </a>
    </div>
    <h3>Tests:</h3>
    <div className="test-buttons">
      <Link to="/Sorter" className="nav-link">
        <button onClick={() => (selectPlaylist('6cmx5OqOJjbRrZjr6HzkF1'))}> Jump to sorter </button>  
      </Link>
    </div>
    {playlists.length != 0 ? (<h2>Playlists:</h2>) : (<></>)}
    {loading ? (
      <div className="loading">Loading...</div>
    ) : (
      <div className="playlists-list">
        {playlists.map((playlist) => (<PlaylistCard key={playlist.id} playlist={playlist} />))}
      </div>)}
  </>
}

export default Home;
