import { BarcodeDetector, prepareZXingModule } from 'barcode-detector/ponyfill'
import django from 'django'
import { useCallback, useEffect, useState } from 'react'
import { BarcodeScanner, type DetectedBarcode } from 'react-barcode-scanner'
import { createRoot } from 'react-dom/client'

const translated = {
  advanced: django.gettext('Advanced'),
  helptext: django.gettext(
    "Choose the type of barcode you want to scan, sometimes this can help if scanning doesn't work."
  ),
  scan_barcode: django.gettext('Scan Barcode'),
  close_barcode: django.gettext('Close Scanner'),
  camera_loading: django.gettext('Opening camera…'),
  insecure_context: django.gettext(
    'Camera access requires HTTPS on a phone. Open this page through a secure HTTPS address.'
  ),
  camera_unavailable: django.gettext(
    'No camera is available, or this browser does not support camera access.'
  ),
  camera_denied: django.gettext(
    'Camera access was denied. Allow camera access in your browser settings, then try again.'
  ),
}

const Scanner = ({
  targetInputId,
  autoOpen = false,
}: {
  targetInputId?: string
  autoOpen?: boolean
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const [isStarting, setIsStarting] = useState(false)
  const [cameraError, setCameraError] = useState('')
  const [selectedFormat, setSelectedFormat] = useState('')
  const defaultFormats = [
    'ean_13',
    'ean_8',
    'upc_a',
    'upc_e',
    'code_39',
    'code_93',
    'code_128',
    'itf',
    'qr_code',
  ]

  const openScanner = useCallback(async () => {
    setCameraError('')

    if (!window.isSecureContext) {
      setCameraError(translated.insecure_context)
      return
    }
    if (!navigator.mediaDevices?.getUserMedia) {
      setCameraError(translated.camera_unavailable)
      return
    }

    setIsStarting(true)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: { facingMode: { ideal: 'environment' } },
      })
      for (const track of stream.getTracks()) {
        track.stop()
      }
      setIsOpen(true)
    } catch (error) {
      const permissionDenied =
        error instanceof DOMException &&
        (error.name === 'NotAllowedError' || error.name === 'SecurityError')
      setCameraError(
        permissionDenied
          ? translated.camera_denied
          : translated.camera_unavailable
      )
    } finally {
      setIsStarting(false)
    }
  }, [])

  useEffect(() => {
    if (autoOpen) {
      openScanner().catch(console.error)
    }
  }, [autoOpen, openScanner])

  const handleCapture = (barcodes: DetectedBarcode[]) => {
    const firstBarcode = barcodes[0]
    if (firstBarcode) {
      const code = firstBarcode.rawValue

      if (targetInputId) {
        const input = document.getElementById(targetInputId) as HTMLInputElement
        if (input) {
          input.value = code
          setIsOpen(false)
        }
      } else {
        window.location.href = `/wine/scan/${code}`
      }
    }
  }
  return (
    <>
      <button
        type="button"
        className="pure-button button__secondary form__scanner__button"
        disabled={isStarting}
        onClick={() => {
          if (isOpen) {
            setIsOpen(false)
          } else {
            openScanner().catch(console.error)
          }
        }}
      >
        {isStarting
          ? translated.camera_loading
          : isOpen
            ? translated.close_barcode
            : translated.scan_barcode}
      </button>
      {cameraError && (
        <p className="scanner-error" role="alert">
          {cameraError}
        </p>
      )}
      {isOpen && (
        <>
          <section className="form__scanner__details">
            <details className="scanner-advanced">
              <summary className="scanner-advanced__summary">
                {translated.advanced}
              </summary>
              <p className="form-hint">{translated.helptext}</p>
              <select
                className="scanner-format-select"
                value={selectedFormat}
                onChange={(e) => setSelectedFormat(e.target.value)}
              >
                <option value="">{django.gettext('All')}</option>
                <option value="code_39">Code 39</option>
                <option value="code_93">Code 93</option>
                <option value="code_128">Code 128</option>
                <option value="ean_8">EAN-8</option>
                <option value="ean_13">EAN-13</option>
                <option value="itf">ITF</option>
                <option value="upc_a">UPC-A</option>
                <option value="upc_e">UPC-E</option>
                <option value="qr_code">QR Code</option>
              </select>
            </details>
          </section>
          <section className="form__scanner">
            <BarcodeScanner
              onCapture={handleCapture}
              options={{
                formats: selectedFormat ? [selectedFormat] : defaultFormats,
              }}
            />
            <div className="scanner-overlay">
              <div className="scanner-overlay__corner scanner-overlay__corner--tl" />
              <div className="scanner-overlay__corner scanner-overlay__corner--tr" />
              <div className="scanner-overlay__corner scanner-overlay__corner--bl" />
              <div className="scanner-overlay__corner scanner-overlay__corner--br" />
            </div>
          </section>
        </>
      )}
    </>
  )
}

const initScanner = () => {
  const container = document.getElementById('scanner')
  if (container) {
    const root = createRoot(container)
    const targetInputId = container.dataset.targetInput
    const autoOpen = container.dataset.autoOpen === 'true'
    // Override the locateFile function
    prepareZXingModule({
      overrides: {
        // @ts-expect-error
        locateFile: (path, prefix) => {
          if (path.endsWith('.wasm')) {
            return container.dataset.zxing_wasm_url
          }
          return prefix + path
        },
      },
    })
    // @ts-expect-error
    globalThis.BarcodeDetector ??= BarcodeDetector
    root.render(<Scanner targetInputId={targetInputId} autoOpen={autoOpen} />)
  }
}

document.addEventListener('DOMContentLoaded', initScanner, false)
