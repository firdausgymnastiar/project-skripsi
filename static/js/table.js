const detail = document.getElementById("detail")
const goBtn = document.getElementById("goBtn")
const tokenInput = document.getElementById("token")
const overlay = document.getElementById("overlay")

function createDescriptionElement(tag, text) {
  const element = document.createElement(tag)
  element.textContent = text
  return element
}

function generateDescription(responseDataKelas) {
  const descriptionList = document.querySelector("#data-list")
  descriptionList.innerHTML = ""

  responseDataKelas.dataKelas.forEach((item) => {
    const dataPairs = [
      ["Token", item[10]],
      ["MATA KULIAH", item[6]],
      ["NAMA DOSEN", item[2]],
      ["PERTEMUAN", `KE-${item[6]}`],
      ["TANGGAL", item[7]],
      ["JAM", item[8]],
      ["DESKRIPSI KELAS", item[9]],
    ]

    dataPairs.forEach(([dtText, ddText]) => {
      descriptionList.appendChild(createDescriptionElement("dt", dtText))
      descriptionList.appendChild(createDescriptionElement("dd", ddText))
    })
  })
}

function generateTable(responseDataKelas) {
  const tableBody = document.querySelector("#data-table tbody")
  tableBody.innerHTML = ""

  responseDataKelas.dataKehadiran.forEach((item, index) => {
    const row = document.createElement("tr")
    row.innerHTML = `
      <td>${index + 1}</td>
      <td>${item[1]}</td>
      <td>${item[2]}</td>
      <td><img src="static/upload/img_login/${
        item[4]
      }" alt="Ini gambar wajah dari mahasiswa dengan nim ${
      item[1]
    }" width="100" height="100"></td>
      <td><img src="static/upload/img_login/${
        item[5]
      }" alt="Ini gambar kelas dari mahasiswa dengan nim ${
      item[1]
    }" width="100" height="100"></td>
      <td>${item[6]}</td>
      <td>hadir cuy</td>
    `
    tableBody.appendChild(row)
  })
}

async function goDetail() {
  const token = tokenInput.value
  overlay.style.display = "flex"

  try {
    const response = await fetch("/generatetable", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ tokenKelas: token }),
    })

    const responseDataKelas = await response.json()

    if (response.ok && responseDataKelas.status === "valid") {
      generateDescription(responseDataKelas)
      generateTable(responseDataKelas)
      overlay.style.display = "none"
      detail.style.display = "block"
    } else {
      alertTable(responseDataKelas)
    }
  } catch (error) {
    console.error("Error fetching data:", error)
    alertTable({ message: "Network error" })
  }
}

function alertTable(responseDataKelas) {
  const { message } = responseDataKelas

  const alertConfig = {
    valid: {
      title: "Kelas Valid!",
      icon: "success",
      text: "Token anda valid",
    },
    "token tidak valid": {
      title: "Token Anda Tidak Valid!",
      icon: "error",
      text: "Mohon ulangi dengan token yang valid",
    },
    "token kosong": {
      title: "Token Kosong!",
      icon: "error",
      text: "Harap masukan token terlebih dahulu",
    },
  }

  const alertSettings = alertConfig[message] || {
    title: "Error!",
    icon: "error",
    text: message,
  }

  Swal.fire({
    icon: alertSettings.icon,
    title: alertSettings.title,
    text: alertSettings.text,
    allowOutsideClick: false,
  }).then((result) => {
    if (result.isConfirmed) {
      overlay.style.display = "none"
    }
  })
}

goBtn.addEventListener("click", goDetail)
