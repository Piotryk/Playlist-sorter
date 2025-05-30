/* eslint-disable no-unused-vars */
import { useState, useEffect } from "react";
import { Routes, Route } from "react-router-dom";
import Home from "../pages/Home";
import Sorter from "../pages/Sorter";
import Debug from "../pages/Debug";
import { SelectedPlaylistProvider } from "./contexts"; 
import './App.css'
import "../css/main.css"

function App() {
  return (
    <>
      <SelectedPlaylistProvider>
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/Sorter" element={<Sorter />} />
            <Route path="/Debug" element={<Debug />} />
          </Routes>
        </main>
      </SelectedPlaylistProvider>
    </>
  )
}

export default App

// 