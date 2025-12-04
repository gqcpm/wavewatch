import React from 'react';
import styled from 'styled-components';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts';
import { theme } from '../../../styles/theme';

const ChartContainer = styled.div`
  background: ${theme.colors.background.primary};
  padding: ${theme.spacing.lg};
  border-radius: ${theme.borderRadius.lg};
  margin: ${theme.spacing.xl} 0;
  border: 1px solid ${theme.colors.border.light};
  box-shadow: ${theme.shadows.md};
`;

const ChartTitle = styled.h4`
  color: ${theme.colors.text.primary};
  margin-bottom: ${theme.spacing.md};
  font-size: ${theme.typography.fontSize.xl};
  font-weight: ${theme.typography.fontWeight.bold};
  font-family: ${theme.typography.fontFamily};
`;

const CustomTooltip = styled.div`
  background: ${theme.colors.background.primary};
  padding: ${theme.spacing.sm};
  border-radius: ${theme.borderRadius.md};
  border: 1px solid ${theme.colors.border.medium};
  color: ${theme.colors.text.primary};
  font-size: ${theme.typography.fontSize.sm};
  box-shadow: ${theme.shadows.lg};
`;

const WaveHeightChart = ({ hourlyForecast, tideData }) => {
  // Transform the hourly forecast data for the chart
  const chartData =
    hourlyForecast?.map((hour, index) => {
      // Format time to HH:MM using built-in Date method
      const time = new Date(hour.time).toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false,
      });
      return {
        time: time,
        waveHeight: parseFloat(hour.waveHeight || hour.wave_height) || 0,
        windSpeed: parseFloat(hour.windSpeed || hour.wind_speed) || 0,
        windDirection: parseFloat(hour.windDirection || hour.wind_direction) || 0,
        airTemperature: parseFloat(hour.airTemperature || hour.air_temperature) || 0,
        fullTime: hour.time,
      };
    }) || [];

  // Transform tide data for chart (high/low points only)
  let tideChartData = [];
  if (
    tideData &&
    tideData.tide_conditions &&
    Array.isArray(tideData.tide_conditions) &&
    tideData.tide_conditions.length > 0
  ) {
    tideChartData = tideData.tide_conditions.map(tide => ({
      time: new Date(tide.time).toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false,
      }),
      tide: parseFloat(tide.tide) || 0,
      fullTime: tide.time,
    }));
  }

  const WaveHeightTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <CustomTooltip>
          <p>
            <strong>Time:</strong> {label}
          </p>
          <p>
            <strong>Wave Height:</strong> {data.waveHeight}ft
          </p>
        </CustomTooltip>
      );
    }
    return null;
  };

  const WindSpeedTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const direction = getWindDirectionText(data.windDirection);
      return (
        <CustomTooltip>
          <p>
            <strong>Time:</strong> {label}
          </p>
          <p>
            <strong>Wind Speed:</strong> {data.windSpeed}mph
          </p>
          <p>
            <strong>Wind Direction:</strong> {direction} ({data.windDirection}°)
          </p>
        </CustomTooltip>
      );
    }
    return null;
  };

  const TideTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <CustomTooltip>
          <p>
            <strong>Time:</strong> {label}
          </p>
          <p>
            <strong>Tide:</strong> {data.tide}ft
          </p>
        </CustomTooltip>
      );
    }
    return null;
  };

  // Helper function to convert wind direction degrees to text
  const getWindDirectionText = degrees => {
    if (degrees >= 337.5 || degrees < 22.5) return 'N';
    if (degrees >= 22.5 && degrees < 67.5) return 'NE';
    if (degrees >= 67.5 && degrees < 112.5) return 'E';
    if (degrees >= 112.5 && degrees < 157.5) return 'SE';
    if (degrees >= 157.5 && degrees < 202.5) return 'S';
    if (degrees >= 202.5 && degrees < 247.5) return 'SW';
    if (degrees >= 247.5 && degrees < 292.5) return 'W';
    if (degrees >= 292.5 && degrees < 337.5) return 'NW';
    return 'N';
  };

  if (!hourlyForecast || hourlyForecast.length === 0) {
    return (
      <ChartContainer>
        <ChartTitle>Wave Height Throughout the Day</ChartTitle>
        <p
          style={{
            color: theme.colors.text.secondary,
            textAlign: 'center',
            padding: theme.spacing.lg,
            fontSize: theme.typography.fontSize.base,
          }}
        >
          No hourly forecast data available
        </p>
      </ChartContainer>
    );
  }

  return (
    <ChartContainer>
      <ChartTitle>📈 Wave Height Throughout the Day</ChartTitle>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart
          data={chartData}
          margin={{
            top: 20,
            right: 30,
            left: 20,
            bottom: 20,
          }}
        >
          <defs>
            <linearGradient id="waveGradient" x1="0" y1="0" x2="0" y2="1">
              <stop
                offset="5%"
                stopColor={theme.colors.accent.blue}
                stopOpacity={0.8}
              />
              <stop
                offset="95%"
                stopColor={theme.colors.accent.blue}
                stopOpacity={0.1}
              />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke={theme.colors.border.light} />
          <XAxis
            dataKey="time"
            stroke={theme.colors.text.secondary}
            fontSize={12}
            tick={{ fill: theme.colors.text.secondary }}
          />
          <YAxis
            stroke={theme.colors.text.secondary}
            fontSize={12}
            tick={{ fill: theme.colors.text.secondary }}
            label={{
              value: 'Wave Height (ft)',
              angle: -90,
              position: 'insideLeft',
              style: { textAnchor: 'middle', fill: theme.colors.text.secondary },
            }}
          />
          <Tooltip content={<WaveHeightTooltip />} />
          <Area
            type="monotone"
            dataKey="waveHeight"
            stroke={theme.colors.accent.blue}
            strokeWidth={3}
            fill="url(#waveGradient)"
            dot={{ fill: theme.colors.accent.blue, strokeWidth: 2, r: 4 }}
            activeDot={{
              r: 6,
              stroke: theme.colors.accent.blue,
              strokeWidth: 2,
              fill: 'white',
            }}
          />
        </AreaChart>
      </ResponsiveContainer>

      {/* Additional chart for wind speed */}
      <div style={{ marginTop: theme.spacing.xl }}>
        <h5
          style={{
            color: theme.colors.text.primary,
            marginBottom: theme.spacing.md,
            fontSize: theme.typography.fontSize.lg,
            fontWeight: theme.typography.fontWeight.bold,
          }}
        >
          Wind Speed
        </h5>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart
            data={chartData}
            margin={{
              top: 20,
              right: 30,
              left: 20,
              bottom: 20,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke={theme.colors.border.light} />
            <XAxis
              dataKey="time"
              stroke={theme.colors.text.secondary}
              fontSize={12}
              tick={{ fill: theme.colors.text.secondary }}
            />
            <YAxis
              stroke={theme.colors.text.secondary}
              fontSize={12}
              tick={{ fill: theme.colors.text.secondary }}
              label={{
                value: 'Wind Speed (mph)',
                angle: -90,
                position: 'insideLeft',
                style: { textAnchor: 'middle', fill: theme.colors.text.secondary },
              }}
            />
            <Tooltip content={<WindSpeedTooltip />} />
            <Line
              type="monotone"
              dataKey="windSpeed"
              stroke={theme.colors.accent.red}
              strokeWidth={2}
              dot={{ fill: theme.colors.accent.red, strokeWidth: 2, r: 3 }}
              activeDot={{
                r: 5,
                stroke: theme.colors.accent.red,
                strokeWidth: 2,
                fill: 'white',
              }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Tide chart - only high/low points with smooth curve */}
      {tideChartData.length > 0 && (
        <div style={{ marginTop: theme.spacing.xl }}>
          <h5
            style={{
              color: theme.colors.text.primary,
              marginBottom: theme.spacing.md,
              fontSize: theme.typography.fontSize.lg,
              fontWeight: theme.typography.fontWeight.bold,
            }}
          >
            Tide (High/Low Points)
          </h5>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart
              data={tideChartData}
              margin={{
                top: 20,
                right: 30,
                left: 20,
                bottom: 20,
              }}
            >
              <defs>
                <linearGradient id="tideGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop
                    offset="5%"
                    stopColor={theme.colors.accent.green}
                    stopOpacity={0.8}
                  />
                  <stop
                    offset="95%"
                    stopColor={theme.colors.accent.green}
                    stopOpacity={0.1}
                  />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke={theme.colors.border.light} />
              <XAxis
                dataKey="time"
                stroke={theme.colors.text.secondary}
                fontSize={12}
                tick={{ fill: theme.colors.text.secondary }}
                interval="preserveStartEnd"
                angle={-45}
                textAnchor="end"
                height={60}
              />
              <YAxis
                stroke={theme.colors.text.secondary}
                fontSize={12}
                tick={{ fill: theme.colors.text.secondary }}
                label={{
                  value: 'Tide (ft)',
                  angle: -90,
                  position: 'insideLeft',
                  style: { textAnchor: 'middle', fill: theme.colors.text.secondary },
                }}
              />
              <Tooltip content={<TideTooltip />} />
              <Area
                type="natural" // Natural spline creates smooth sinusoidal curve through points
                dataKey="tide"
                stroke={theme.colors.accent.green}
                strokeWidth={2}
                fill="url(#tideGradient)"
                dot={{ fill: theme.colors.accent.green, strokeWidth: 2, r: 5 }} // Visible dots for high/low points
                activeDot={{
                  r: 7,
                  stroke: theme.colors.accent.green,
                  strokeWidth: 2,
                  fill: 'white',
                }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </ChartContainer>
  );
};

export default WaveHeightChart;
