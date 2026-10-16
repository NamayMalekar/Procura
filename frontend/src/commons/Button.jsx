export default function Button({ variant = '', size = '', ...props }) {
  return <button className={`btn ${variant} ${size}`} {...props} />
}
