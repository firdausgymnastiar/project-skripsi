const formLogin = document.getElementById("formLogin")
const tokenInput = document.getElementById("tokenKelas")
const validateTokenBtn = document.getElementById("validateTokenBtn")
const gambarWajah = document.getElementById("gambarWajah")
const cameraButton = document.getElementById("cameraButton")
const ulangiCamera = document.getElementById("ulangiCamera")
const preview = document.getElementById("preview")
const validateWajahBtn = document.getElementById("validateWajahBtn")
const gambarKelas = document.getElementById("gambarKelas")
const cameraButton2 = document.getElementById("cameraButton2")
const ulangiCamera2 = document.getElementById("ulangiCamera2")
const preview2 = document.getElementById("preview2")
const validateKelasBtn = document.getElementById("validateKelasBtn")
const submitButton = document.getElementById("submitButton")
const overlay = document.getElementById("overlay")
const sectionWajah = document.getElementById("sectionWajah")
const sectionKelas = document.getElementById("sectionKelas")
const sectionSubmit = document.getElementById("sectionSubmit")

let isTokenValidated = false
let isWajahValidated = false
let isKelasValidated = false

function checkFormValidity() {
  if (isTokenValidated && isWajahValidated && isKelasValidated) {
    submitButton.disabled = false
  } else {
    submitButton.disabled = true
  }
}

let validatedToken = null
async function validateToken() {
  const token = tokenInput.value
  // if (!token) {
  //   alert("Token is required")
  //   return
  // }
  // Tampilkan overlay saat memulai submit form
  overlay.style.display = "flex"
  const response = await fetch("/validate_token", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ tokenKelas: token }),
  })

  const responseDataToken = await response.json()
  if (response.ok && responseDataToken.status === "valid") {
    alertToken(responseDataToken)
    validatedToken = token // Simpan file gambar wajah yang valid
    isTokenValidated = true
    sectionWajah.style.display = "block"
    tokenInput.disabled = true
    validateTokenBtn.disabled = true
    cameraButton.disabled = false
    ulangiCamera.disabled = false
    validateWajahBtn.disabled = false
    cameraButton2.disabled = true
    ulangiCamera2.disabled = true
    validateKelasBtn.disabled = true
  } else {
    alertToken(responseDataToken)
    isTokenValidated = false
    cameraButton.disabled = true
    ulangiCamera.disabled = true
    validateWajahBtn.disabled = true
    cameraButton2.disabled = true
    ulangiCamera2.disabled = true
    validateKelasBtn.disabled = true
  }
  checkFormValidity()
}
function alertToken(responseDataToken) {
  let message = responseDataToken.message
  let token = responseDataToken.token

  let alertTitle, alertIcon, alertText

  switch (message) {
    case "token valid":
      alertTitle = "Token Anda Valid"
      alertIcon = "success"
      alertText = `Token ${token} Valid, Mohon lanjutkan validasi gambar!`
      break
    case "token tidak valid":
      alertTitle = "Token Anda Tidak Valid"
      alertIcon = "error"
      alertText = `Token ${tokenInput.value} Tidak Valid, Mohon Ulangi!`
      break
    case "token kosong":
      alertTitle = "Tidak Ada Token Yang Di Input"
      alertIcon = "error"
      alertText = "Masukan Token Anda"
      break
    default:
      alertTitle = "Error!"
      alertIcon = "error"
      alertText = "Terjadi kesalahan saat menyimpan data"
      break
  }
  Swal.fire({
    icon: alertIcon,
    title: alertTitle,
    text: alertText,
    allowOutsideClick: false,
  }).then((result) => {
    if (result.isConfirmed) {
      // tokenInput.value = ""
      // Tampilkan overlay saat memulai submit form
      overlay.style.display = "none"
    }
  })
}

let validatedWajahFile = null
let validatedNIM = null
async function validateWajah() {
  const input = gambarWajah
  const file = input.files[0]

  // if (!file) {
  //   alert("Please select a file")
  //   return
  // }
  overlay.style.display = "flex"
  const formData = new FormData()
  formData.append("file", file)

  const response = await fetch("/validate_image_wajah", {
    method: "POST",
    body: formData,
  })

  const responseDataWajah = await response.json()
  if (response.ok && responseDataWajah.status === "valid") {
    alertWajah(responseDataWajah)
    validatedWajahFile = file // Simpan file gambar wajah yang valid
    validatedNIM = responseDataWajah.nim // Simpan file gambar wajah yang valid
    isWajahValidated = true
    sectionKelas.style.display = "block"
    tokenInput.disabled = true
    validateTokenBtn.disabled = true
    cameraButton.disabled = true
    ulangiCamera.disabled = true
    validateWajahBtn.disabled = true
    cameraButton2.disabled = false
    ulangiCamera2.disabled = false
    validateKelasBtn.disabled = false
  } else {
    alertWajah(responseDataWajah)

    isWajahValidated = false
    tokenInput.disabled = true
    validateTokenBtn.disabled = true
    cameraButton.disabled = false
    ulangiCamera.disabled = false
    validateWajahBtn.disabled = false
    cameraButton2.disabled = true
    ulangiCamera2.disabled = true
    validateKelasBtn.disabled = true
  }
  checkFormValidity()
}

function alertWajah(responseDataWajah) {
  let message = responseDataWajah.message
  let nim = responseDataWajah.nim

  let alertTitle, alertIcon, alertText

  switch (message) {
    case "successfull":
      alertTitle = "Wajah Valid!"
      alertIcon = "success"
      alertText = `Wajah anda terdaftar dengan nim: ${nim}!`
      break
    case "No file part":
      alertTitle = "File Gambar Tidak Ada!"
      alertIcon = "error"
      alertText = "Mohon ambil gambar terlebih dahulu!"
      break
    case "you are not registered yet":
      alertTitle = "Wajah Anda Belum Terdaftar!"
      alertIcon = "error"
      alertText = "Mohon lakukan registrasi wajah terlebih dahulu!"
      break
    case "More than 1 face detected":
      alertTitle = "Terdeteksi Lebih Dari 1 Wajah!"
      alertIcon = "error"
      alertText = "Mohon ambil gambar hanya 1 wajah saja!"
      break
    case "there is no one face detected":
      alertTitle = "Wajah Tidak Terdeteksi!"
      alertIcon = "error"
      alertText = "Wajah anda tidak terdeteksi, mohon ulangi!"
      break
    case "fake":
      alertTitle = "Terindikasi Palsu!"
      alertIcon = "error"
      alertText = "Mohon ulangi dengan wajah yang asli!"
      break
    case "gada didaftar db!":
      alertTitle = "Error!"
      alertIcon = "error"
      alertText = "Wajah terdaftar tetapi tidak tersedia di database"
      break
    case "Missing required data":
      alertTitle = "Format foto tidak diizinkan!"
      alertIcon = "error"
      alertText =
        "Format foto yang diizinkan hanya .jpg/.jpeg/.png . Mohon Ulangi!"
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

let validatedKelasFile = null
async function validateKelas() {
  const input = gambarKelas
  const file = input.files[0]

  // if (!file) {
  //   alert("Please select a file")
  //   return
  // }

  overlay.style.display = "flex"

  const formData = new FormData()
  formData.append("file", file)

  const response = await fetch("/validate_image_kelas", {
    method: "POST",
    body: formData,
  })

  const responseDataKelas = await response.json()
  if (response.ok && responseDataKelas.success === true) {
    alertKelas(responseDataKelas)
    validatedKelasFile = file // Simpan file gambar wajah yang valid
    isKelasValidated = true
    sectionSubmit.style.display = "block"
    tokenInput.disabled = true
    validateTokenBtn.disabled = true
    cameraButton.disabled = true
    ulangiCamera.disabled = true
    validateWajahBtn.disabled = true
    cameraButton2.disabled = true
    ulangiCamera2.disabled = true
    validateKelasBtn.disabled = true
  } else {
    alertKelas(responseDataKelas)
    isKelasValidated = false
    tokenInput.disabled = true
    validateTokenBtn.disabled = true
    cameraButton.disabled = true
    ulangiCamera.disabled = true
    validateWajahBtn.disabled = true
    cameraButton2.disabled = false
    ulangiCamera2.disabled = false
    validateKelasBtn.disabled = false
  }
  checkFormValidity()
}

function alertKelas(responseDataKelas) {
  let message = responseDataKelas.message
  let confidence = responseDataKelas.confidence

  let alertTitle, alertIcon, alertText

  switch (message) {
    case "Classroom":
      alertTitle = "Ruang Kelas Terdeteksi!"
      alertIcon = "success"
      alertText = `Anda terdeteksi di ruang kelas, silahkan submit untuk kehadiran anda!`
      break
    case "Not A Classroom":
      alertTitle = "Ruang Kelas Tidak Terdeteksi!"
      alertIcon = "error"
      alertText = `${confidence}% yakin gambar yang diinput bukan gambar ruang kelas`
      break
    case "No file part":
      alertTitle = "File Gambar Tidak Ada!"
      alertIcon = "error"
      alertText = "Mohon ambil gambar terlebih dahulu!"
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

validateTokenBtn.addEventListener("click", validateToken)
validateWajahBtn.addEventListener("click", validateWajah)
validateKelasBtn.addEventListener("click", validateKelas)
formLogin.addEventListener("submit", simpanData)

cameraButton.addEventListener("click", function () {
  gambarWajah.click()
})

ulangiCamera.addEventListener("click", function () {
  gambarWajah.click()
})

gambarWajah.addEventListener("change", function () {
  if (gambarWajah.files && gambarWajah.files[0]) {
    cameraButton.style.display = "none"
    ulangiCamera.style.display = "block"
    validateWajahBtn.style.display = "block"
    const reader = new FileReader()
    reader.onload = function (e) {
      preview.src = e.target.result
      preview.style.display = "block"
    }
    reader.readAsDataURL(gambarWajah.files[0])
  }
})

cameraButton2.addEventListener("click", function () {
  gambarKelas.click()
})

ulangiCamera2.addEventListener("click", function () {
  gambarKelas.click()
})

gambarKelas.addEventListener("change", function () {
  if (gambarKelas.files && gambarKelas.files[0]) {
    cameraButton2.style.display = "none"
    ulangiCamera2.style.display = "block"
    validateKelasBtn.style.display = "block"
    const reader = new FileReader()
    reader.onload = function (e) {
      preview2.src = e.target.result
      preview2.style.display = "block"
    }
    reader.readAsDataURL(gambarKelas.files[0])
  }
})

async function simpanData(event) {
  event.preventDefault() // Prevent the default form submission behavior

  console.log("Token:", validatedToken)
  console.log("Wajah:", validatedWajahFile)
  console.log("NIM:", validatedNIM)
  console.log("Kelas:", validatedKelasFile)

  token = validatedToken
  wajah = validatedWajahFile
  kelas = validatedKelasFile
  nim = validatedNIM

  overlay.style.display = "flex"
  if (!token || !wajah || !kelas) {
    displayAlert("Token, wajah, dan kelas harus diisi.")
    return
  }

  // const token = tokenInput.value
  // const inputWajah = gambarWajah
  // const fileWajah = inputWajah.files[0]
  // const inputKelas = gambarKelas
  // const fileKelas = inputKelas.files[0]

  const formData = new FormData(formLogin)
  formData.append("token", token)
  formData.append("gambarWajah", wajah)
  formData.append("gambarKelas", kelas)
  // Buat objek JSON untuk nim
  // const jsonNim = JSON.stringify({ nim: nim })

  // Tambahkan JSON nim ke FormData sebagai blob
  // formData.append("nim", new Blob([jsonNim], { type: "application/json" }))
  formData.append("nim", nim) // Tambahkan nim ke FormData

  const response = await fetch("/loginkelas", {
    method: "POST",
    body: formData,
  })

  const responseData = await response.json()
  try {
    if (response.ok && responseData.success) {
      displayAlert(responseData)
    } else {
      displayAlert(responseData.error_message || responseData)
    }
  } catch (error) {
    displayAlert("Terjadi kesalahan dalam mengirim permintaan")
    console.error("Error:", error)
  }
}

function displayAlert(responseData) {
  let message = responseData.message
  let nim = responseData.nim
  let token = responseData.token
  let name = responseData.name

  let alertTitle, alertIcon, alertText

  switch (message) {
    case "Missing required data":
      alertTitle = "Formulir Tidak Lengkap!"
      alertIcon = "error"
      alertText = "Mohon isi formulir dengan lengkap!"
      break
    case "successfull":
      alertTitle = "Login Berhasil"
      alertIcon = "success"
      alertText = `Selamat Datang ${name}(NIM: ${nim}) di kelas dengan token: ${token}!`
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
      window.location.href = "/table"
    }
  })
}
