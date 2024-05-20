const detail = document.getElementById("detail")
const goBtn = document.getElementById("goBtn")
const tokenInput = document.getElementById("token")
const overlay = document.getElementById("overlay")

function generateDescription(responseDataKelas) {
  const descriptionList = document.querySelector("#data-list")
  descriptionList.innerHTML = "" // Clear existing data
  responseDataKelas.dataKelas.forEach((item, index) => {
    const dtToken = document.createElement("dt")
    dtToken.textContent = `Token`
    descriptionList.appendChild(dtToken)

    const ddToken = document.createElement("dd")
    ddToken.textContent = `${item[10]}`
    descriptionList.appendChild(ddToken)

    const dtMatkul = document.createElement("dt")
    dtMatkul.textContent = "MATA KULIAH"
    descriptionList.appendChild(dtMatkul)

    const ddMatkul = document.createElement("dd")
    ddMatkul.textContent = `${item[6]}`
    descriptionList.appendChild(ddMatkul)

    const dtNamaDosen = document.createElement("dt")
    dtNamaDosen.textContent = "NAMA DOSEN"
    descriptionList.appendChild(dtNamaDosen)

    const ddNamaDosen = document.createElement("dd")
    ddNamaDosen.textContent = `${item[2]}`
    descriptionList.appendChild(ddNamaDosen)

    const dtPertemuan = document.createElement("dt")
    dtPertemuan.textContent = "PERTEMUAN"
    descriptionList.appendChild(dtPertemuan)

    const ddPertemuan = document.createElement("dd")
    ddPertemuan.textContent = `KE-${item[6]}`
    descriptionList.appendChild(ddPertemuan)

    const dtTanggal = document.createElement("dt")
    dtTanggal.textContent = "TANGGAL"
    descriptionList.appendChild(dtTanggal)

    const ddTanggal = document.createElement("dd")
    ddTanggal.textContent = `${item[7]}`
    descriptionList.appendChild(ddTanggal)

    const dtTimes = document.createElement("dt")
    dtTimes.textContent = "JAM"
    descriptionList.appendChild(dtTimes)

    const ddTimes = document.createElement("dd")
    ddTimes.textContent = `${item[8]}`
    descriptionList.appendChild(ddTimes)

    const dtDeskripsi = document.createElement("dt")
    dtDeskripsi.textContent = "DESKRIPSI KELAS"
    descriptionList.appendChild(dtDeskripsi)

    const ddDeskripsi = document.createElement("dd")
    ddDeskripsi.textContent = `${item[9]}`
    descriptionList.appendChild(ddDeskripsi)
  })
}

function generateTable(responseDataKelas) {
  const tableBody = document.querySelector("#data-table tbody")
  tableBody.innerHTML = "" // Clear existing data
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
}

function alertTable(responseDataKelas) {
  let message = responseDataKelas.message

  let alertTitle, alertIcon, alertText

  switch (message) {
    case "valid":
      alertTitle = "Kelas Valid!"
      alertIcon = "success"
      alertText = "token anda valid"
      break
    case "token tidak valid":
      alertTitle = "Token Anda Tidak Valid!"
      alertIcon = "error"
      alertText = "Mohon ulangi dengan token yang valid"
      break
    case "token kosong":
      alertTitle = "Token Kosong!"
      alertIcon = "error"
      alertText = "Harap masukan token terlebih dahulu"
      break
    default:
      alertTitle = "Error!"
      alertIcon = "error"
      alertText = message
      break
  }
  Swal.fire({
    icon: alertIcon,
    title: alertTitle,
    text: alertText,
    allowOutsideClick: false,
  }).then((result) => {
    if (result.isConfirmed) {
      // window.location.href = "/login"
      overlay.style.display = "none"
    }
  })
}
goBtn.addEventListener("click", goDetail)
