import { BarcodeDetector, prepareZXingModule } from 'barcode-detector/ponyfill'
import django from 'django'
import { useCallback, useEffect, useRef, useState } from 'react'
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
  label_search: django.gettext(
    'No code found. Hold the bottle label steady inside the frame.'
  ),
  label_ready: django.gettext('Label detected. Keep still…'),
  label_uploading: django.gettext('Photo captured. Analysing the label…'),
  label_failed: django.gettext(
    'The automatic label analysis failed. You can try again or upload a photo manually.'
  ),
  take_photo: django.gettext('Take photo'),
  retry: django.gettext('Try again'),
  manual_upload: django.gettext('Upload a photo'),
}

const analyseFrame = (
  video: HTMLVideoElement,
  canvas: HTMLCanvasElement,
  previousFrame?: Uint8ClampedArray
) => {
  const width = 160
  const height = 120
  canvas.width = width
  canvas.height = height
  const context = canvas.getContext('2d', { willReadFrequently: true })
  if (!context) {
    return undefined
  }
  context.drawImage(video, 0, 0, width, height)
  const image = context.getImageData(0, 0, width, height)
  const grayscale = new Uint8ClampedArray(width * height)
  let sum = 0
  let sumSquares = 0
  let edges = 0
  let motion = 0
  let samples = 0

  for (let y = 24; y < height - 24; y += 2) {
    for (let x = 32; x < width - 32; x += 2) {
      const pixel = y * width + x
      const offset = pixel * 4
      const value =
        image.data[offset]! * 0.299 +
        image.data[offset + 1]! * 0.587 +
        image.data[offset + 2]! * 0.114
      grayscale[pixel] = value
      sum += value
      sumSquares += value * value
      if (x > 32) {
        edges += Math.abs(value - grayscale[pixel - 2]!)
      }
      if (previousFrame) {
        motion += Math.abs(value - previousFrame[pixel]!)
      }
      samples += 1
    }
  }

  const mean = sum / samples
  return {
    frame: grayscale,
    variance: sumSquares / samples - mean * mean,
    edgeStrength: edges / samples,
    motion: previousFrame ? motion / samples : Number.POSITIVE_INFINITY,
  }
}

const Scanner = ({
  targetInputId,
  autoOpen = false,
  labelCapture = false,
  aiEnabled = false,
  aiUploadUrl = '',
  csrfToken = '',
}: {
  targetInputId?: string
  autoOpen?: boolean
  labelCapture?: boolean
  aiEnabled?: boolean
  aiUploadUrl?: string
  csrfToken?: string
}) => {
  const scannerRef = useRef<HTMLDivElement>(null)
  const isUploadingRef = useRef(false)
  const [isOpen, setIsOpen] = useState(false)
  const [isStarting, setIsStarting] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [cameraError, setCameraError] = useState('')
  const [stableFrames, setStableFrames] = useState(0)
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

  const uploadLabel = useCallback(async () => {
    if (isUploadingRef.current) {
      return
    }
    const video = scannerRef.current?.querySelector('video')
    if (!video || video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA) {
      return
    }
    if (!aiEnabled || !aiUploadUrl) {
      window.location.href = aiUploadUrl || '/wine/ai/'
      return
    }

    isUploadingRef.current = true
    setIsUploading(true)
    setCameraError('')
    const scale = Math.min(1, 1280 / video.videoWidth)
    const canvas = document.createElement('canvas')
    canvas.width = Math.round(video.videoWidth * scale)
    canvas.height = Math.round(video.videoHeight * scale)
    const context = canvas.getContext('2d')
    context?.drawImage(video, 0, 0, canvas.width, canvas.height)

    try {
      const blob = await new Promise<Blob>((resolve, reject) => {
        canvas.toBlob(
          (result) =>
            result
              ? resolve(result)
              : reject(new Error('Image capture failed')),
          'image/jpeg',
          0.88
        )
      })
      const body = new FormData()
      body.append('front', blob, 'label.jpg')
      const response = await fetch(aiUploadUrl, {
        method: 'POST',
        body,
        headers: {
          'X-CSRFToken': csrfToken,
          'X-Requested-With': 'XMLHttpRequest',
        },
      })
      if (response.redirected) {
        window.location.href = response.url
        return
      }
      throw new Error(`AI upload failed with status ${response.status}`)
    } catch (error) {
      console.error(error)
      setCameraError(translated.label_failed)
      setIsUploading(false)
      isUploadingRef.current = false
      setStableFrames(0)
    }
  }, [aiEnabled, aiUploadUrl, csrfToken])

  useEffect(() => {
    if (!isOpen || !labelCapture || isUploading) {
      return
    }
    const canvas = document.createElement('canvas')
    let previousFrame: Uint8ClampedArray | undefined
    let stable = 0
    const interval = window.setInterval(() => {
      const video = scannerRef.current?.querySelector('video')
      if (!video || video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA) {
        return
      }
      const analysis = analyseFrame(video, canvas, previousFrame)
      previousFrame = analysis?.frame
      if (
        analysis &&
        analysis.variance > 650 &&
        analysis.edgeStrength > 10 &&
        analysis.motion < 5
      ) {
        stable += 1
      } else {
        stable = 0
      }
      setStableFrames(stable)
      if (stable >= 5) {
        window.clearInterval(interval)
        uploadLabel().catch(console.error)
      }
    }, 500)
    return () => window.clearInterval(interval)
  }, [isOpen, isUploading, labelCapture, uploadLabel])

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
        const params = new URLSearchParams({ code })
        window.location.href = `/wine/scan?${params.toString()}`
      }
    }
  }
  return (
    <div ref={scannerRef}>
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
        <div className="scanner-error" role="alert">
          <p>{cameraError}</p>
          {labelCapture && (
            <div className="scanner-error__actions">
              <button
                type="button"
                onClick={() => uploadLabel().catch(console.error)}
              >
                {translated.retry}
              </button>
              <a href={aiUploadUrl}>{translated.manual_upload}</a>
            </div>
          )}
        </div>
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
            {labelCapture && (
              <div className="scanner-label-status" aria-live="polite">
                {isUploading
                  ? translated.label_uploading
                  : stableFrames > 1
                    ? translated.label_ready
                    : translated.label_search}
              </div>
            )}
          </section>
          {labelCapture && !isUploading && (
            <button
              type="button"
              className="pure-button button__secondary scanner-photo-button"
              onClick={() => uploadLabel().catch(console.error)}
            >
              {translated.take_photo}
            </button>
          )}
        </>
      )}
    </div>
  )
}

const initScanner = () => {
  const container = document.getElementById('scanner')
  if (container) {
    const root = createRoot(container)
    const targetInputId = container.dataset.targetInput
    const autoOpen = container.dataset.autoOpen === 'true'
    const labelCapture = container.dataset.labelCapture === 'true'
    const aiEnabled = container.dataset.aiEnabled === 'true'
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
    root.render(
      <Scanner
        targetInputId={targetInputId}
        autoOpen={autoOpen}
        labelCapture={labelCapture}
        aiEnabled={aiEnabled}
        aiUploadUrl={container.dataset.aiUploadUrl}
        csrfToken={container.dataset.csrfToken}
      />
    )
  }
}

document.addEventListener('DOMContentLoaded', initScanner, false)
