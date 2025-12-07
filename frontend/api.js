let userId = null;
const API = "http://localhost:8000/api";

function getCheckedTopics() {
    return [...document.querySelectorAll("input[type=checkbox]:checked")]
        .map(cb => cb.value);
}

async function createUser() {
    const email = document.getElementById("email").value;

    const res = await fetch(`${API}/users`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email })
    });

    const data = await res.json();

    if (res.ok) {
        userId = data.user_id;
        document.getElementById("userResult").innerText =
            `User created. UserID = ${userId}`;
    } else {
        alert(data.detail);
    }
}

async function updateTopics() {
    if (!userId) return alert("Create a user first!");

    const topics = getCheckedTopics();

    const res = await fetch(`${API}/users/${userId}/topics`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topics })
    });

    const data = await res.json();
    document.getElementById("topicsResult").innerText =
        `Saved topics: ${data.interested_topics.join(", ")}`;
}

async function addLocation() {
    if (!userId) return alert("Create a user first!");

    const label = document.getElementById("locLabel").value;
    const address = document.getElementById("locAddress").value;
    const radius_miles = Number(document.getElementById("locRadius").value);

    const res = await fetch(`${API}/users/${userId}/locations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ label, address, radius_miles })
    });

    const data = await res.json();

    document.getElementById("locationList").innerText +=
        `Added: ${data.label} (${data.address})\n`;
}

async function loadItems() {
    if (!userId) return alert("Create a user first!");

    const res = await fetch(`${API}/users/${userId}/items`);
    const data = await res.json();

    document.getElementById("itemsPreview").innerText =
        JSON.stringify(data, null, 2);
}

async function sendDigest() {
    if (!userId) return alert("Create a user first!");

    const res = await fetch(`${API}/users/${userId}/send_digest`, {
        method: "POST"
    });

    const data = await res.json();

    document.getElementById("digestResult").innerText =
        `Sent email to: ${data.sent_to} | Items: ${data.item_count}`;
}
