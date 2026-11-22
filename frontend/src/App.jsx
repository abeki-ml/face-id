import { useEffect, useRef, useState } from "react";

// Where our Python server lives
const API = "http://localhost:8000";

export default function App() {
  const videoRef = useRef(null);
  const [name, setName] = useState("");
  const [message, setMessage] = useState("");
  const [good, setGood] = useState(false);
  const [busy, setBusy] = useState(false);

  // Start the camera when the page opens
  useEffect(() => {
    let stream;

    async function startCamera() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: true,
        });

        videoRef.current.srcObject = stream;
      } catch (error) {
        setGood(false);
        setMessage("Could not open the camera. Allow camera access, then refresh the page.");
      }
    }

    startCamera();

    return () => {
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  // Take a picture from the camera
  function takePhoto() {
    const video = videoRef.current;
    const canvas = document.createElement("canvas");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    canvas.getContext("2d").drawImage(video, 0, 0);

    return new Promise((resolve) => {
      canvas.toBlob(resolve, "image/jpeg", 0.9);
    });
  }

  // Send the picture to the backend
  async function send(action) {
    if (busy) return;

    if (action === "register" && name.trim() === "") {
      setGood(false);
      setMessage("Please enter your name before registering.");
      return;
    }

    setBusy(true);
    setMessage("");

    try {
      const photo = await takePhoto();

      if (!photo) {
        throw new Error("Could not capture photo.");
      }

      const form = new FormData();

      if (action === "register") {
        form.append("name", name.trim());
      }

      form.append("photo", photo, "photo.jpg");

      const response = await fetch(`${API}/${action}`, {
        method: "POST",
        body: form,
      });

      const data = await response.json();

      if (!response.ok) {
        setGood(false);
        setMessage(data.detail || "Something went wrong.");
      } else if (action === "register") {
        setGood(true);
        setMessage(data.message);
      } else {
        setGood(data.match);

        setMessage(
          data.match
            ? `Welcome, ${data.name} (score ${data.score})`
            : `Face not recognised (score ${data.score})`
        );
      }
    } catch (error) {
      setGood(false);
      setMessage("Could not reach the server. Is it running on port 8000?");
    }

    setBusy(false);
  }

  return (
    <div
      style={{
        maxWidth: 480,
        margin: "20px auto",
        fontFamily: "sans-serif",
        padding: 12,
      }}
    >
      <h1>Face ID</h1>

      <input
        value={name}
        onChange={(event) => setName(event.target.value)}
        placeholder="Your name, e.g. amina"
        style={{
          width: "100%",
          padding: 10,
          fontSize: 16,
          boxSizing: "border-box",
        }}
      />

      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        style={{
          width: "100%",
          background: "#000",
          marginTop: 12,
        }}
      />

      <button
        onClick={() => send("register")}
        disabled={busy}
        style={{ padding: "10px 18px", fontSize: 16, marginRight: 8 }}
      >
        Register
      </button>

      <button
        onClick={() => send("verify")}
        disabled={busy}
        style={{ padding: "10px 18px", fontSize: 16 }}
      >
        Verify
      </button>

      {message && (
        <p style={{ color: good ? "green" : "crimson", fontSize: 18 }}>
          {message}
        </p>
      )}
    </div>
  );
}