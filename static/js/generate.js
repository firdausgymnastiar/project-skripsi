const formGenerate = document.getElementById("formGenerate")

function generateRandomNumber() {
  // Membuat angka acak antara 100000 dan 999999 (6 digit)
  var randomNumber = Math.floor(100000 + Math.random() * 900000)
  // Menampilkan angka acak di console
  console.log("Angka acak: " + randomNumber)
  // Menampilkan angka acak di halaman HTML
  document.getElementById("randomNumberDisplay").value = randomNumber
}

async function sendToServer() {
  const formData = new FormData(formGenerate)

  document.getElementById("overlay").style.display = "flex"

  const response = await fetch("/generatetoken", {
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
    console.log("ada error:")
    displayAlert("Terjadi kesalahan dalam mengirim permintaan")
    console.error("Error:", error)
  }
}

formGenerate.addEventListener("submit", function (event) {
  event.preventDefault()
  sendToServer()
})

// Fungsi untuk menampilkan SweetAlert berdasarkan pesan dari server
function displayAlert(responseData) {
  let message = responseData.message // Mengambil nilai dari kunci 'message'
  let token = responseData.token // Mengambil nilai dari kunci 'token'

  let alertTitle, alertIcon, alertText

  // Menyesuaikan judul dan ikon berdasarkan pesan dari server
  switch (message) {
    case "Missing required data":
      alertTitle = "Formulir Tidak Lengkap!"
      alertIcon = "error"
      alertText = "Mohon isi formulir dengan lengkap!"
      break
    case "successfull":
      alertTitle = "Token Berhasil Diaktifkan!"
      alertIcon = "success"
      alertText = `Token Anda Adalah: <strong id="token">${token}</strong> <button id="copy-btn" type="button" class="btn btn-success btn-sm">Copy</button>`
      break
    case "token is existing":
      alertTitle = "Token Sudah Ada!"
      alertIcon = "error"
      alertText = "Maaf token sudah ada, mohon generate ulang!"
      break
    case "gagal pas di mysql token":
      alertTitle = "Error!"
      alertIcon = "error"
      alertText = "gagal pas di mysql token"
      break
    case "gagal pas di mysql":
      alertTitle = "Error!"
      alertIcon = "error"
      alertText = "gagal pas di mysql"
      break
    case "Terjadi kesalahan dalam mengirim permintaan":
      alertTitle = "Error!"
      alertIcon = "error"
      alertText = "Terjadi kesalahan dalam mengirim permintaan"
      break
    case "form kosong":
      alertTitle = "Error!"
      alertIcon = "error"
      alertText = "Form kosong/terjadi kesalahan, mohon ulangi!"
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
    html: alertText,
    allowOutsideClick: false,
    showConfirmButton: true,
    didRender: () => {
      // Tambahkan event listener untuk tombol salin setelah SweetAlert dirender
      const copyButton = document.getElementById("copy-btn")
      if (copyButton) {
        copyButton.addEventListener("click", () => {
          const tokenElement = document.getElementById("token")
          if (tokenElement) {
            const textToCopy = tokenElement.innerText
            const textarea = document.createElement("textarea")
            textarea.value = textToCopy
            document.body.appendChild(textarea)
            textarea.select()
            document.execCommand("copy")
            document.body.removeChild(textarea)

            // Menampilkan notifikasi bahwa teks telah disalin
            Swal.fire({
              icon: "success",
              title: "Copied!",
              text: "Token telah disalin ke clipboard.",
              allowOutsideClick: false,
              // timer: 1500,
              showConfirmButton: true,
            }).then((result) => {
              // Setelah mengklik tombol "OK"
              if (result.isConfirmed) {
                window.location.href = "/generate"
              }
            })
          }
        })
      }
    },
  }).then((result) => {
    // Setelah mengklik tombol "OK"
    if (result.isConfirmed) {
      window.location.href = "/generate"
    }
  })
}
