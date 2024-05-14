const formLogin = document.getElementById("formLogin")
// Menangkap elemen input dan tombol
const gambarWajah = document.getElementById("gambarWajah")
const cameraButton = document.getElementById("cameraButton")
const ulangiCamera = document.getElementById("ulangiCamera")
const preview = document.getElementById("preview")

var token = document.getElementById("tokenKelas")

async function sendToServer() {
  const formData = new FormData(formLogin)

  // Tampilkan overlay saat memulai submit form
  document.getElementById("overlay").style.display = "flex"

  const response = await fetch("/loginkelas", {
    method: "POST",
    body: formData,
  })
  const responseData = await response.json()
  try {
    if (response.ok && responseData.success) {
      displayAlert(responseData)
    } else {
      // Jika permintaan gagal atau respons dari Flask menunjukkan kegagalan
      displayAlert(responseData.error_message || responseData)
    }
  } catch (error) {
    // Jika terjadi kesalahan dalam melakukan permintaan
    displayAlert("Terjadi kesalahan dalam mengirim permintaan")
    console.error("Error:", error)
  }
}

formLogin.addEventListener("submit", function (event) {
  event.preventDefault()
  sendToServer()
})

// Menambahkan event listener untuk tombol
cameraButton.addEventListener("click", function () {
  // Membuka kamera saat tombol ditekan
  gambarWajah.click()
})
// Menambahkan event listener untuk tombol
ulangiCamera.addEventListener("click", function () {
  // Membuka kamera saat tombol ditekan
  gambarWajah.click()
})
// Menambahkan event listener ketika gambar dipilih
gambarWajah.addEventListener("change", function () {
  // Memastikan ada file yang dipilih
  if (gambarWajah.files && gambarWajah.files[0]) {
    cameraButton.style.display = "none"
    ulangiCamera.style.display = "block"
    const reader = new FileReader()
    reader.onload = function (e) {
      // Menampilkan gambar yang dipilih sebagai preview
      preview.src = e.target.result
    }
    // Membaca file gambar yang dipilih sebagai URL data
    reader.readAsDataURL(gambarWajah.files[0])
  }
})

// Fungsi untuk menampilkan SweetAlert berdasarkan pesan dari server
function displayAlert(responseData) {
  let message = responseData.message // Mengambil nilai dari kunci 'message'
  let name = responseData.name // Mengambil nilai dari kunci 'nim'

  let alertTitle, alertIcon, alertText

  // Menyesuaikan judul dan ikon berdasarkan pesan dari server
  switch (message) {
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
    case "there is no one face detected":
      alertTitle = "Wajah Tidak Terdeteksi!"
      alertIcon = "error"
      alertText = "Wajah anda tidak terdeteksi, mohon ulangi!"
      break
    case "More than 1 face detected":
      alertTitle = "Terdeteksi Lebih Dari 1 Wajah!"
      alertIcon = "error"
      alertText = "Mohon ambil gambar hanya 1 wajah saja!"
      break
    case "No selected file":
      alertTitle = "Gambar Tidak Dipilih!"
      alertIcon = "error"
      alertText = "Mohon pilih gambar terlebih dahulu!"
      break
    case "Missing required data":
      alertTitle = "Formulir Tidak Lengkap!"
      alertIcon = "error"
      alertText = "Mohon isi formulir dengan lengkap!"
      break
    case "gada didaftar db!":
      alertTitle = "Error!"
      alertIcon = "error"
      alertText = "Wajah terdaftar tetapi tidak tersedia di database"
      break
    case "successfull":
      alertTitle = "Login Berhasil"
      alertIcon = "success"
      alertText = `Selamat Datang ${name}!`
      break
    case "Terjadi kesalahan dalam mengirim permintaan":
      alertTitle = "Error!"
      alertIcon = "error"
      alertText = "Terjadi kesalahan dalam mengirim permintaan"
      break
    case "form kosong":
      alertTitle = "Error!"
      alertIcon = "error"
      alertText = "Form kosong / terjadi kesalahan, mohon ulangi!"
      break
    case "fake":
      alertTitle = "Terindikasi Palsu!"
      alertIcon = "error"
      alertText = "Mohon ulangi dengan wajah yang asli!"
      break
    default:
      alertTitle = "Error!"
      alertIcon = "error"
      alertText = "Terjadi kesalahan saat menyimpan data"
      break
  }

  // Menampilkan SweetAlert
  Swal.fire({
    icon: alertIcon,
    title: alertTitle,
    text: alertText,
    allowOutsideClick: false, // Mengizinkan menutup alert dengan mengklik di luar kotak alert
  }).then((result) => {
    // Setelah mengklik tombol "OK"
    if (result.isConfirmed) {
      window.location.href = "/login"
    }
  })
}
