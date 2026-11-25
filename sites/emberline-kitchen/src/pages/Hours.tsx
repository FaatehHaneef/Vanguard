import { Accordion } from '../components/Accordion'
import { Icon } from '../components/Icon'
import { usePage } from '../lib/page'

const hours = [
  { day: 'Monday', kitchen: 'Closed', pickup: 'No orders' },
  { day: 'Tuesday', kitchen: '12:00 to 22:00', pickup: '12:00 to 21:30' },
  { day: 'Wednesday', kitchen: '12:00 to 22:00', pickup: '12:00 to 21:30' },
  { day: 'Thursday', kitchen: '12:00 to 22:00', pickup: '12:00 to 21:30' },
  { day: 'Friday', kitchen: '12:00 to 22:00', pickup: '12:00 to 21:30' },
  { day: 'Saturday', kitchen: '12:00 to 22:00', pickup: '12:00 to 21:30' },
  { day: 'Sunday', kitchen: '12:00 to 22:00', pickup: '12:00 to 21:30' },
]

function MapArt() {
  return (
    <svg className="map-art" viewBox="0 0 480 300" role="img" aria-labelledby="map-title">
      <title id="map-title">
        Street map: Emberline Kitchen is on Copper Street, at the corner with Mill Lane, two minutes
        from Harwick station
      </title>
      <rect width="480" height="300" fill="#f4e6d0" />
      <rect x="0" y="120" width="480" height="40" fill="#fffaf3" />
      <rect x="200" y="0" width="36" height="300" fill="#fffaf3" />
      <rect x="0" y="236" width="480" height="18" fill="#ead5b6" />
      <rect x="30" y="24" width="140" height="74" rx="8" fill="#9ccc8f" />
      <rect x="262" y="24" width="190" height="74" rx="8" fill="#ead5b6" />
      <rect x="30" y="180" width="140" height="42" rx="8" fill="#ead5b6" />
      <rect x="262" y="180" width="80" height="42" rx="8" fill="#ead5b6" />
      <rect x="360" y="262" width="100" height="30" rx="6" fill="#3d2c24" />
      <text x="410" y="282" fill="#fffaf3" fontSize="13" textAnchor="middle" fontFamily="sans-serif">
        Station
      </text>
      <text x="100" y="146" fill="#6b5a51" fontSize="14" fontFamily="sans-serif">
        Copper Street
      </text>
      <text x="246" y="290" fill="#6b5a51" fontSize="13" fontFamily="sans-serif" transform="rotate(-90 246 290)">
        Mill Lane
      </text>
      <circle cx="252" cy="118" r="16" fill="#c2410c" />
      <circle cx="252" cy="118" r="6" fill="#fffaf3" />
    </svg>
  )
}

export function Hours() {
  const heading = usePage('Hours & location')
  return (
    <>
      <section className="container page-head">
        <p className="eyebrow">Visit us</p>
        <h1 ref={heading} tabIndex={-1}>
          Opening hours and how to find us
        </h1>
        <p className="lead">
          The kitchen is open six days a week. Pickup orders can be collected until half an hour
          before we close.
        </p>
      </section>

      <section className="container hours-layout">
        <div className="panel">
          <h2>Opening hours</h2>
          <table className="hours-table">
            <caption className="visually-hidden">Kitchen and pickup hours by day</caption>
            <thead>
              <tr>
                <th scope="col">Day</th>
                <th scope="col">Kitchen</th>
                <th scope="col">Pickup orders</th>
              </tr>
            </thead>
            <tbody>
              {hours.map((row) => (
                <tr key={row.day}>
                  <th scope="row">{row.day}</th>
                  <td>{row.kitchen}</td>
                  <td>{row.pickup}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="muted">
            Bank holidays: open as usual, except Christmas Day and Boxing Day when we are closed.
          </p>
        </div>

        <div className="panel">
          <h2>Where we are</h2>
          <MapArt />
          <ul className="contact-list">
            <li>
              <Icon name="pin" /> 14 Copper Street, Harwick HW2 4LT
            </li>
            <li>
              <Icon name="phone" /> 01632 960214
            </li>
            <li>
              <Icon name="clock" /> Most orders are ready about 20 minutes after you place them
            </li>
          </ul>
        </div>
      </section>

      <section className="container section" aria-labelledby="getting-here">
        <h2 id="getting-here">Getting here</h2>
        <Accordion
          items={[
            {
              title: 'By train',
              body: (
                <p>
                  Harwick station is a two-minute walk. Leave by the Mill Lane exit, turn left and we
                  are on the corner with Copper Street.
                </p>
              ),
            },
            {
              title: 'By bus',
              body: (
                <p>
                  The 12 and 31 stop outside the station. The 7 stops on Copper Street itself, at the
                  stop called Market Cross.
                </p>
              ),
            },
            {
              title: 'Parking',
              body: (
                <p>
                  There are three short-stay spaces outside the shop, free for 20 minutes. The Mill
                  Lane car park is a minute away and charges £1.20 an hour.
                </p>
              ),
            },
            {
              title: 'Step-free access',
              body: (
                <p>
                  The counter is at street level with a level entrance. The door is 90 cm wide. Ring
                  the bell by the door if you would like us to bring your order out.
                </p>
              ),
            },
          ]}
        />
      </section>
    </>
  )
}
